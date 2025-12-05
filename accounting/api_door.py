# accounting/api_door.py
"""
REST API endpoints for Tasmota door control.
JWT authenticated for React frontend.
"""

import requests
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger(__name__)

# Tasmota configuration from settings
TASMOTA_IP = getattr(settings, 'TASMOTA_IP', '192.168.1.100')
TASMOTA_PORT = getattr(settings, 'TASMOTA_PORT', 80)
TIMEOUT = 5


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def door_status(request):
    """
    Get door relay status.
    GET /api/v1/door/status/

    Returns:
        - success: bool
        - status: "open" | "closed" | "error"
        - raw_power: "ON" | "OFF"
        - online: bool
    """
    try:
        url = f"http://{TASMOTA_IP}:{TASMOTA_PORT}/cm?cmnd=Power"

        logger.info(f"Checking door status at {TASMOTA_IP}")
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            power = data.get("POWER", "OFF")

            logger.info(f"Door status: {power}")

            return Response({
                'success': True,
                'status': 'open' if power == 'ON' else 'closed',
                'raw_power': power,
                'online': True
            })
        else:
            return Response({
                'success': False,
                'status': 'error',
                'online': False,
                'message': 'Αποτυχία επικοινωνίας με τη συσκευή'
            }, status=500)

    except requests.exceptions.Timeout:
        logger.warning(f"Door status timeout at {TASMOTA_IP}")
        return Response({
            'success': False,
            'status': 'error',
            'online': False,
            'message': 'Timeout - η συσκευή δεν απαντά'
        }, status=504)
    except requests.exceptions.ConnectionError:
        logger.warning(f"Door connection error at {TASMOTA_IP}")
        return Response({
            'success': False,
            'status': 'error',
            'online': False,
            'message': 'Δεν βρέθηκε η συσκευή'
        }, status=503)
    except Exception as e:
        logger.error(f"Door status error: {e}")
        return Response({
            'success': False,
            'status': 'error',
            'online': False,
            'message': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def door_open(request):
    """
    Open/toggle the door via Tasmota relay.
    POST /api/v1/door/open/

    Returns:
        - success: bool
        - message: str (Greek)
        - new_status: "open" | "closed"
    """
    try:
        # Toggle the relay
        url = f"http://{TASMOTA_IP}:{TASMOTA_PORT}/cm?cmnd=Power%20Toggle"

        logger.info(f"User {request.user.username} toggling door at {TASMOTA_IP}")
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            new_power = data.get("POWER", "OFF")

            logger.info(f"Door toggled by {request.user.username}, new state: {new_power}")

            return Response({
                'success': True,
                'message': 'Η πόρτα άνοιξε!' if new_power == 'ON' else 'Η πόρτα έκλεισε!',
                'new_status': 'open' if new_power == 'ON' else 'closed'
            })
        else:
            return Response({
                'success': False,
                'message': 'Αποτυχία επικοινωνίας με τη συσκευή'
            }, status=500)

    except requests.exceptions.Timeout:
        logger.warning(f"Door toggle timeout for user {request.user.username}")
        return Response({
            'success': False,
            'message': 'Timeout - η συσκευή δεν απαντά'
        }, status=504)
    except requests.exceptions.ConnectionError:
        logger.warning(f"Door toggle connection error for user {request.user.username}")
        return Response({
            'success': False,
            'message': 'Δεν βρέθηκε η συσκευή'
        }, status=503)
    except Exception as e:
        logger.error(f"Door toggle error for user {request.user.username}: {e}")
        return Response({
            'success': False,
            'message': f'Σφάλμα: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def door_pulse(request):
    """
    Pulse the door relay (momentary on for electric locks).
    POST /api/v1/door/pulse/

    Optional body:
        - duration: int (seconds, default 1)

    Returns:
        - success: bool
        - message: str (Greek)
    """
    try:
        duration = request.data.get('duration', 1)
        pulse_time = int(duration) * 10  # Tasmota uses deciseconds

        # Set pulse time
        set_pulse_url = f"http://{TASMOTA_IP}:{TASMOTA_PORT}/cm?cmnd=PulseTime1%20{pulse_time}"
        requests.get(set_pulse_url, timeout=TIMEOUT)

        # Trigger pulse
        pulse_url = f"http://{TASMOTA_IP}:{TASMOTA_PORT}/cm?cmnd=Power%20ON"

        logger.info(f"User {request.user.username} pulsing door for {duration}s")
        response = requests.get(pulse_url, timeout=TIMEOUT)

        if response.status_code == 200:
            logger.info(f"Door pulsed by {request.user.username}")
            return Response({
                'success': True,
                'message': f'Πόρτα ανοιχτή για {duration} δευτ.'
            })
        else:
            return Response({
                'success': False,
                'message': 'Αποτυχία επικοινωνίας με τη συσκευή'
            }, status=500)

    except requests.exceptions.Timeout:
        return Response({
            'success': False,
            'message': 'Timeout - η συσκευή δεν απαντά'
        }, status=504)
    except requests.exceptions.ConnectionError:
        return Response({
            'success': False,
            'message': 'Δεν βρέθηκε η συσκευή'
        }, status=503)
    except Exception as e:
        logger.error(f"Door pulse error: {e}")
        return Response({
            'success': False,
            'message': f'Σφάλμα: {str(e)}'
        }, status=500)
