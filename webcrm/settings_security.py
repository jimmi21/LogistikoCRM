"""
Security settings for LogistikoCRM.

These settings are loaded based on DEBUG mode:
- DEBUG=True: Development settings (relaxed)
- DEBUG=False: Production settings (strict)

IMPORTANT: This file should be imported AFTER main settings.py
"""
import os
from django.core.exceptions import ImproperlyConfigured


def configure_security_settings(settings_module):
    """
    Configure security settings based on DEBUG mode.
    Call this at the end of settings.py.
    """
    DEBUG = getattr(settings_module, 'DEBUG', False)

    if not DEBUG:
        # =====================================================
        # PRODUCTION SECURITY SETTINGS
        # =====================================================

        # Require SECRET_KEY from environment
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'default-key-for-development':
            raise ImproperlyConfigured(
                'SECRET_KEY environment variable is REQUIRED in production! '
                'Generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
            )

        # HSTS (HTTP Strict Transport Security)
        settings_module.SECURE_HSTS_SECONDS = 31536000  # 1 year
        settings_module.SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        settings_module.SECURE_HSTS_PRELOAD = True

        # HTTPS redirect
        settings_module.SECURE_SSL_REDIRECT = True

        # Secure cookies
        settings_module.SESSION_COOKIE_SECURE = True
        settings_module.CSRF_COOKIE_SECURE = True
        settings_module.SESSION_COOKIE_HTTPONLY = True

        # Security headers
        settings_module.SECURE_CONTENT_TYPE_NOSNIFF = True
        settings_module.SECURE_BROWSER_XSS_FILTER = True
        settings_module.X_FRAME_OPTIONS = 'DENY'

        # Proxy settings (if behind nginx/load balancer)
        settings_module.SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        settings_module.USE_X_FORWARDED_HOST = True

        # CORS - strict origins only
        settings_module.CORS_ALLOW_ALL_ORIGINS = False

        print("[SECURITY] Production security settings enabled")

    else:
        # =====================================================
        # DEVELOPMENT SECURITY SETTINGS
        # =====================================================

        # Relaxed settings for development
        settings_module.SECURE_HSTS_SECONDS = 0
        settings_module.SECURE_SSL_REDIRECT = False
        settings_module.SESSION_COOKIE_SECURE = False
        settings_module.CSRF_COOKIE_SECURE = False

        # Still enable HttpOnly for session cookies (good practice)
        settings_module.SESSION_COOKIE_HTTPONLY = True

        # Allow all origins in development
        settings_module.CORS_ALLOW_ALL_ORIGINS = True

        print("[SECURITY] Development security settings (relaxed)")


# =====================================================
# RATE LIMITING SETTINGS
# =====================================================
RATE_LIMIT_SETTINGS = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',       # Anonymous users: 100 requests/hour
        'user': '1000/hour',      # Authenticated users: 1000 requests/hour
        'login': '5/minute',      # Login attempts: 5/minute
        'door': '10/hour',        # Door control: 10/hour
    }
}


# =====================================================
# FILE UPLOAD SECURITY SETTINGS
# =====================================================
FILE_UPLOAD_SETTINGS = {
    # Maximum upload size (10MB)
    'MAX_UPLOAD_SIZE': 10 * 1024 * 1024,

    # Allowed file extensions
    'ALLOWED_EXTENSIONS': [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.jpg', '.jpeg', '.png', '.gif',
        '.txt', '.csv', '.zip', '.rar',
    ],

    # Blocked extensions (executables)
    'BLOCKED_EXTENSIONS': [
        '.exe', '.sh', '.bat', '.cmd', '.com', '.msi',
        '.vbs', '.js', '.jar', '.py', '.php', '.asp',
    ],

    # Allowed MIME types
    'ALLOWED_MIME_TYPES': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/jpeg', 'image/png', 'image/gif',
        'text/plain', 'text/csv',
        'application/zip', 'application/x-rar-compressed',
    ],
}


# =====================================================
# CACHING SETTINGS
# =====================================================
def get_cache_settings(redis_url=None):
    """
    Returns cache settings based on available backend.

    Args:
        redis_url: Redis URL (e.g., 'redis://localhost:6379/1')

    Returns:
        CACHES dict for Django settings
    """
    if redis_url:
        return {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': redis_url,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'SOCKET_CONNECT_TIMEOUT': 5,
                    'SOCKET_TIMEOUT': 5,
                    'RETRY_ON_TIMEOUT': True,
                    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                },
                'KEY_PREFIX': 'logistikocrm',
            },
            # Separate cache for sessions
            'sessions': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': redis_url.replace('/1', '/2') if '/1' in redis_url else redis_url + '/2',
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                },
                'KEY_PREFIX': 'sessions',
            }
        }
    else:
        # Fallback to database cache
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                'LOCATION': 'django_cache_table',
            }
        }
