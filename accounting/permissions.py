# -*- coding: utf-8 -*-
"""
accounting/permissions.py
Author: ddiplas
Description: Custom permissions for VoIP and internal services
"""
from rest_framework.permissions import BasePermission
from django.conf import settings


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
            return False

        # Get expected token from settings
        expected_token = getattr(settings, 'FRITZ_API_TOKEN', None)

        if not expected_token:
            return False

        # Secure comparison to prevent timing attacks
        return api_key == expected_token
