# -*- coding: utf-8 -*-
"""
Email Utilities for LogistikoCRM
Author: Claude
Version: 1.0
Description: Retry logic, rate limiting, and connection pooling for email sending.
"""

import functools
import logging
import time
import threading
from smtplib import (
    SMTPException,
    SMTPServerDisconnected,
    SMTPAuthenticationError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
    SMTPDataError,
    SMTPConnectError,
)
from socket import timeout as SocketTimeout, error as SocketError
from ssl import SSLError
from django.core.mail import get_connection
from django.conf import settings

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class EmailError(Exception):
    """Base exception for email errors"""
    def __init__(self, message: str, original_error: Exception = None, attempt: int = 0):
        self.message = message
        self.original_error = original_error
        self.attempt = attempt
        super().__init__(self.message)


class EmailConnectionError(EmailError):
    """Network/connection errors (retriable)"""
    pass


class EmailAuthError(EmailError):
    """Authentication errors (NOT retriable)"""
    pass


class EmailRateLimitError(EmailError):
    """Rate limit exceeded"""
    pass


class EmailPermanentError(EmailError):
    """Permanent errors that should not be retried"""
    pass


# =============================================================================
# RETRY DECORATOR
# =============================================================================

# Exceptions that should be retried
RETRIABLE_EXCEPTIONS = (
    SMTPServerDisconnected,
    SMTPConnectError,
    SMTPDataError,  # Sometimes transient
    SocketTimeout,
    SocketError,
    SSLError,
    ConnectionError,
    ConnectionResetError,
    BrokenPipeError,
    TimeoutError,
    OSError,  # Catch-all for network issues
)

# Exceptions that should NOT be retried
PERMANENT_EXCEPTIONS = (
    SMTPAuthenticationError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
    ValueError,
)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    retriable_exceptions: tuple = RETRIABLE_EXCEPTIONS,
    permanent_exceptions: tuple = PERMANENT_EXCEPTIONS,
):
    """
    Decorator for retry with exponential backoff.

    Delays: 2s, 4s, 8s, 16s (max 30s)
    Retries only on network/transient errors.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        retriable_exceptions: Tuple of exception types to retry
        permanent_exceptions: Tuple of exception types to NOT retry

    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except permanent_exceptions as e:
                    # Don't retry permanent errors
                    logger.error(f"Email permanent error (no retry): {str(e)}")
                    raise EmailPermanentError(
                        message=f"Permanent email error: {str(e)}",
                        original_error=e,
                        attempt=attempt
                    )

                except retriable_exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(
                            f"📧 Email retry {attempt + 1}/{max_retries} "
                            f"after {delay:.1f}s delay. Error: {type(e).__name__}: {str(e)}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"📧 Email failed after {max_retries} retries: "
                            f"{type(e).__name__}: {str(e)}"
                        )

                except SMTPException as e:
                    # Catch any other SMTP exceptions
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(
                            f"📧 Email retry {attempt + 1}/{max_retries} "
                            f"(SMTP error) after {delay:.1f}s. Error: {str(e)}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"📧 Email failed after retries: {str(e)}")

            # Raise the last exception if all retries failed
            if last_exception:
                raise EmailConnectionError(
                    message=f"Email failed after {max_retries} retries: {str(last_exception)}",
                    original_error=last_exception,
                    attempt=max_retries
                )

        return wrapper
    return decorator


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Thread-safe rate limiter for email sending.
    Default: 2 emails per second (conservative for most SMTP servers)

    Gmail limits: 100/day (regular), 500/day (Google Workspace)
    SMTP servers typically allow 2-5 req/sec
    """

    def __init__(self, requests_per_second: float = 2.0, burst_size: int = 5):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum sustained rate
            burst_size: Number of requests allowed in burst
        """
        self.min_interval = 1.0 / requests_per_second
        self.burst_size = burst_size
        self.last_request_time = 0.0
        self.request_count = 0
        self.window_start = 0.0
        self._lock = threading.Lock()

    def wait(self) -> float:
        """
        Wait if needed to respect rate limit.

        Returns:
            float: Time waited in seconds
        """
        with self._lock:
            now = time.time()

            # Reset window if more than 1 second has passed
            if now - self.window_start >= 1.0:
                self.window_start = now
                self.request_count = 0

            # Check burst limit
            if self.request_count >= self.burst_size:
                wait_time = 1.0 - (now - self.window_start)
                if wait_time > 0:
                    logger.debug(f"Rate limiter: waiting {wait_time:.3f}s (burst limit)")
                    time.sleep(wait_time)
                    now = time.time()
                    self.window_start = now
                    self.request_count = 0

            # Check minimum interval
            elapsed = now - self.last_request_time
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                logger.debug(f"Rate limiter: waiting {wait_time:.3f}s")
                time.sleep(wait_time)
                now = time.time()

            self.last_request_time = now
            self.request_count += 1
            return now - (now - elapsed if elapsed < self.min_interval else now)

    def reset(self):
        """Reset the rate limiter state"""
        with self._lock:
            self.last_request_time = 0.0
            self.request_count = 0
            self.window_start = 0.0


# Global rate limiter instance
_rate_limiter = None
_rate_limiter_lock = threading.Lock()


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        with _rate_limiter_lock:
            if _rate_limiter is None:
                # Get rate from settings or use default
                rate = getattr(settings, 'EMAIL_RATE_LIMIT', 2.0)
                burst = getattr(settings, 'EMAIL_BURST_LIMIT', 5)
                _rate_limiter = RateLimiter(
                    requests_per_second=rate,
                    burst_size=burst
                )
    return _rate_limiter


# =============================================================================
# CONNECTION POOL
# =============================================================================

class EmailConnectionPool:
    """
    Thread-safe connection pool for SMTP connections.
    Reuses connections for bulk email sending to reduce overhead.
    """

    def __init__(self, max_connections: int = 3, connection_ttl: float = 300.0):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum number of pooled connections
            connection_ttl: Time-to-live for connections in seconds (default 5 min)
        """
        self.max_connections = max_connections
        self.connection_ttl = connection_ttl
        self._pool = []  # List of (connection, creation_time) tuples
        self._lock = threading.Lock()
        self._active_count = 0

    def get_connection(self):
        """
        Get a connection from the pool or create a new one.

        Returns:
            Django email backend connection
        """
        with self._lock:
            now = time.time()

            # Try to get an existing connection
            while self._pool:
                conn, created_at = self._pool.pop(0)

                # Check if connection is still valid (not expired)
                if now - created_at < self.connection_ttl:
                    try:
                        # Test connection by checking if it's open
                        if hasattr(conn, 'connection') and conn.connection:
                            self._active_count += 1
                            return conn
                    except Exception:
                        # Connection is stale, close and get new one
                        try:
                            conn.close()
                        except Exception:
                            pass
                else:
                    # Connection expired, close it
                    try:
                        conn.close()
                    except Exception:
                        pass

            # Create new connection
            self._active_count += 1

        # Create connection outside the lock
        conn = get_connection(
            backend=getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
            fail_silently=False
        )

        try:
            conn.open()
        except Exception as e:
            with self._lock:
                self._active_count -= 1
            raise

        return conn

    def return_connection(self, conn):
        """
        Return a connection to the pool for reuse.

        Args:
            conn: Django email backend connection
        """
        with self._lock:
            self._active_count -= 1

            # Only pool if we haven't exceeded max
            if len(self._pool) < self.max_connections:
                self._pool.append((conn, time.time()))
            else:
                # Close excess connections
                try:
                    conn.close()
                except Exception:
                    pass

    def close_connection(self, conn):
        """
        Close a connection (don't return to pool).

        Args:
            conn: Django email backend connection
        """
        with self._lock:
            self._active_count -= 1

        try:
            conn.close()
        except Exception:
            pass

    def close_all(self):
        """Close all pooled connections"""
        with self._lock:
            for conn, _ in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool.clear()

    @property
    def stats(self) -> dict:
        """Get pool statistics"""
        with self._lock:
            return {
                'pooled': len(self._pool),
                'active': self._active_count,
                'max': self.max_connections,
            }


# Global connection pool instance
_connection_pool = None
_connection_pool_lock = threading.Lock()


def get_connection_pool() -> EmailConnectionPool:
    """Get or create the global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        with _connection_pool_lock:
            if _connection_pool is None:
                max_conn = getattr(settings, 'EMAIL_POOL_MAX_CONNECTIONS', 3)
                ttl = getattr(settings, 'EMAIL_POOL_CONNECTION_TTL', 300.0)
                _connection_pool = EmailConnectionPool(
                    max_connections=max_conn,
                    connection_ttl=ttl
                )
    return _connection_pool


# =============================================================================
# CONTEXT MANAGER FOR BULK SENDING
# =============================================================================

class BulkEmailSender:
    """
    Context manager for efficient bulk email sending.
    Uses connection pooling and rate limiting.

    Usage:
        with BulkEmailSender() as sender:
            for email in emails:
                sender.send(email)
    """

    def __init__(self, use_pool: bool = True, use_rate_limit: bool = True):
        """
        Initialize bulk sender.

        Args:
            use_pool: Whether to use connection pooling
            use_rate_limit: Whether to apply rate limiting
        """
        self.use_pool = use_pool
        self.use_rate_limit = use_rate_limit
        self._connection = None
        self._pool = None
        self._rate_limiter = None
        self._sent_count = 0
        self._failed_count = 0

    def __enter__(self):
        if self.use_pool:
            self._pool = get_connection_pool()
            self._connection = self._pool.get_connection()
        else:
            self._connection = get_connection(fail_silently=False)
            self._connection.open()

        if self.use_rate_limit:
            self._rate_limiter = get_rate_limiter()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            if self.use_pool and self._pool:
                if exc_type is None:
                    self._pool.return_connection(self._connection)
                else:
                    self._pool.close_connection(self._connection)
            else:
                try:
                    self._connection.close()
                except Exception:
                    pass

        return False  # Don't suppress exceptions

    def send(self, email_message) -> bool:
        """
        Send a single email message.

        Args:
            email_message: Django EmailMessage instance

        Returns:
            bool: True if sent successfully
        """
        if self._rate_limiter:
            self._rate_limiter.wait()

        try:
            # Use the pooled connection
            email_message.connection = self._connection
            sent = email_message.send(fail_silently=False)
            self._sent_count += 1
            return sent > 0
        except Exception as e:
            self._failed_count += 1
            raise

    @property
    def stats(self) -> dict:
        """Get sending statistics"""
        return {
            'sent': self._sent_count,
            'failed': self._failed_count,
            'total': self._sent_count + self._failed_count,
        }
