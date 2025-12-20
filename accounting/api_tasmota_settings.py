# -*- coding: utf-8 -*-
"""
API endpoints for Tasmota Settings.
Allows frontend to retrieve and update Tasmota configuration.
"""
import requests
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import TasmotaSettings

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasmota_settings_get(request):
    """
    Get current Tasmota settings.
    GET /api/v1/settings/tasmota/

    Returns:
        - ip_address: str
        - port: int
        - device_name: str
        - is_enabled: bool
        - timeout: int
    """
    settings = TasmotaSettings.get_settings()

    return Response({
        'ip_address': settings.ip_address,
        'port': settings.port,
        'device_name': settings.device_name,
        'is_enabled': settings.is_enabled,
        'timeout': settings.timeout,
        'updated_at': settings.updated_at.isoformat() if settings.updated_at else None,
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def tasmota_settings_update(request):
    """
    Update Tasmota settings (admin only).
    PUT /api/v1/settings/tasmota/

    Body:
        - ip_address: str (optional)
        - port: int (optional)
        - device_name: str (optional)
        - is_enabled: bool (optional)
        - timeout: int (optional)

    Returns updated settings.
    """
    settings = TasmotaSettings.get_settings()

    # Update fields if provided
    if 'ip_address' in request.data:
        settings.ip_address = request.data['ip_address']
    if 'port' in request.data:
        settings.port = int(request.data['port'])
    if 'device_name' in request.data:
        settings.device_name = request.data['device_name']
    if 'is_enabled' in request.data:
        settings.is_enabled = bool(request.data['is_enabled'])
    if 'timeout' in request.data:
        settings.timeout = int(request.data['timeout'])

    settings.save()

    logger.info(f"Tasmota settings updated by {request.user.username}: IP={settings.ip_address}")

    return Response({
        'success': True,
        'message': 'Οι ρυθμίσεις αποθηκεύτηκαν',
        'ip_address': settings.ip_address,
        'port': settings.port,
        'device_name': settings.device_name,
        'is_enabled': settings.is_enabled,
        'timeout': settings.timeout,
        'updated_at': settings.updated_at.isoformat() if settings.updated_at else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def tasmota_settings_test(request):
    """
    Test connection to Tasmota device.
    POST /api/v1/settings/tasmota/test/

    Optional body:
        - ip_address: str (test specific IP instead of saved)
        - port: int

    Returns:
        - success: bool
        - online: bool
        - message: str
        - device_info: dict (if online)
    """
    settings = TasmotaSettings.get_settings()

    # Allow testing a different IP without saving
    ip = request.data.get('ip_address', settings.ip_address)
    port = int(request.data.get('port', settings.port))
    timeout = int(request.data.get('timeout', settings.timeout))

    url = f"http://{ip}:{port}/cm?cmnd=Status"

    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            status_info = data.get('Status', {})

            return Response({
                'success': True,
                'online': True,
                'message': 'Συνδέθηκε επιτυχώς!',
                'device_info': {
                    'device_name': status_info.get('DeviceName', 'Unknown'),
                    'power': 'ON' if status_info.get('Power', 0) else 'OFF',
                    'friendly_name': status_info.get('FriendlyName', [''])[0] if status_info.get('FriendlyName') else '',
                }
            })
        else:
            return Response({
                'success': False,
                'online': False,
                'message': f'HTTP Error {response.status_code}'
            })

    except requests.exceptions.Timeout:
        return Response({
            'success': False,
            'online': False,
            'message': f'Timeout - η συσκευή δεν απάντησε σε {timeout} δευτερόλεπτα'
        })
    except requests.exceptions.ConnectionError:
        return Response({
            'success': False,
            'online': False,
            'message': f'Δεν βρέθηκε συσκευή στη διεύθυνση {ip}:{port}'
        })
    except Exception as e:
        logger.error(f"Tasmota test error: {e}")
        return Response({
            'success': False,
            'online': False,
            'message': f'Σφάλμα: {str(e)}'
        })
