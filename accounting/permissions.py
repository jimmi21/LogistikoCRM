# -*- coding: utf-8 -*-
"""
accounting/permissions.py
Author: ddiplas
Description: Custom permissions for VoIP and internal services
"""
import logging
from rest_framework.permissions import BasePermission
from django.conf import settings

logger = logging.getLogger(__name__)


class IsVoIPMonitor(BasePermission):
    """
    Custom permission for VoIP monitor services (e.g., Fritz!Box monitor).

    Allows access if the request includes a valid X-API-Key header
    matching the FRITZ_API_TOKEN setting.

    Usage in ViewSet:
        permission_classes = [IsAuthenticated | IsVoIPMonitor]
    """

    def has_permission(self, request, view):
        # Get API key from header or query parameter
        api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')

        if not api_key:
            logger.debug(f"IsVoIPMonitor: Denied - No X-API-Key header or api_key param (IP: {self._get_client_ip(request)})")
            return False

        # Get expected token from settings
        expected_token = getattr(settings, 'FRITZ_API_TOKEN', None)

        if not expected_token:
            logger.warning("IsVoIPMonitor: Denied - FRITZ_API_TOKEN not configured in settings")
            return False

        # Secure comparison to prevent timing attacks
        if api_key == expected_token:
            logger.debug(f"IsVoIPMonitor: Granted - Valid API key (IP: {self._get_client_ip(request)})")
            return True
        else:
            # Log mismatch with masked tokens for debugging
            provided_masked = api_key[:4] + '...' if len(api_key) > 4 else '****'
            expected_masked = expected_token[:4] + '...' if len(expected_token) > 4 else '****'
            logger.warning(
                f"IsVoIPMonitor: Denied - Token mismatch "
                f"(provided: {provided_masked}, expected: {expected_masked}, IP: {self._get_client_ip(request)})"
            )
            return False

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class IsLocalRequest(BasePermission):
    """
    Permission that allows requests from localhost/loopback addresses.

    Useful as a fallback for internal services running on the same machine.

    Allowed IPs:
    - 127.0.0.1 (IPv4 loopback)
    - localhost (resolved)
    - ::1 (IPv6 loopback)

    Usage in ViewSet:
        permission_classes = [IsAuthenticated | IsVoIPMonitor | IsLocalRequest]
    """

    ALLOWED_IPS = {'127.0.0.1', 'localhost', '::1'}

    def has_permission(self, request, view):
        client_ip = self._get_client_ip(request)

        if client_ip in self.ALLOWED_IPS:
            logger.debug(f"IsLocalRequest: Granted - Local request from {client_ip}")
            return True

        logger.debug(f"IsLocalRequest: Denied - Non-local IP: {client_ip}")
        return False

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        # For local requests, don't use X-Forwarded-For (could be spoofed)
        return request.META.get('REMOTE_ADDR', 'unknown')
