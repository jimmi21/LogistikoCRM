# accounting/api_door.py
"""
REST API endpoints for Tasmota door control.
JWT authenticated for React frontend.

Security features:
- Rate limiting (10 actions per minute per user)
- Audit logging for all door actions
- Staff-only access for door control

Configuration is stored in database via TasmotaSettings model.
"""

import requests
import logging
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response

from .models import TasmotaSettings

logger = logging.getLogger(__name__)


def get_tasmota_config():
    """Get Tasmota configuration from database"""
    settings = TasmotaSettings.get_settings()
    return {
        'ip': settings.ip_address,
        'port': settings.port,
        'timeout': settings.timeout,
        'enabled': settings.is_enabled,
        'base_url': settings.base_url,
        'device_name': settings.device_name,
    }


class DoorActionThrottle(UserRateThrottle):
    """
    Rate limit for door control actions.
    Prevents abuse - max 10 door actions per minute per user.
    """
    rate = '10/minute'
    scope = 'door_action'


class DoorStatusThrottle(UserRateThrottle):
    """
    Rate limit for door status checks.
    More lenient - max 30 status checks per minute.
    """
    rate = '30/minute'
    scope = 'door_status'


def log_door_access(request, action, result, response_data=None):
    """Log door access to audit trail"""
    try:
        from .models import DoorAccessLog
        DoorAccessLog.log_access(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            result=result,
            request=request,
            response_data=response_data
        )
    except Exception as e:
        logger.error(f"Failed to log door access: {e}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([DoorStatusThrottle])
def door_status(request):
    """
    Get door relay status.
    GET /api/v1/door/status/

    Returns:
        - success: bool
        - status: "open" | "closed" | "error" | "disabled"
        - raw_power: "ON" | "OFF"
        - online: bool
        - device_name: str
        - enabled: bool
    """
    config = get_tasmota_config()

    # Check if door control is enabled
    if not config['enabled']:
        return Response({
            'success': True,
            'status': 'disabled',
            'online': False,
            'enabled': False,
            'device_name': config['device_name'],
            'message': 'Ο έλεγχος πόρτας είναι απενεργοποιημένος'
        })

    try:
        url = f"{config['base_url']}/cm?cmnd=Power"

        logger.info(f"Checking door status at {config['ip']}")
        response = requests.get(url, timeout=config['timeout'])

        if response.status_code == 200:
            data = response.json()
            power = data.get("POWER", "OFF")

            logger.info(f"Door status: {power}")

            response_data = {
                'success': True,
                'status': 'open' if power == 'ON' else 'closed',
                'raw_power': power,
                'online': True,
                'enabled': True,
                'device_name': config['device_name'],
            }
            log_door_access(request, 'status', 'success', response_data)
            return Response(response_data)
        else:
            response_data = {
                'success': False,
                'status': 'offline',
                'online': False,
                'enabled': True,
                'device_name': config['device_name'],
                'message': 'Αποτυχία επικοινωνίας με τη συσκευή'
            }
            log_door_access(request, 'status', 'failed', response_data)
            return Response(response_data)

    except requests.exceptions.Timeout:
        logger.debug(f"Door status timeout at {config['ip']}")
        response_data = {
            'success': False,
            'status': 'offline',
            'online': False,
            'enabled': True,
            'device_name': config['device_name'],
            'message': 'Timeout - η συσκευή δεν απαντά'
        }
        log_door_access(request, 'status', 'timeout', response_data)
        return Response(response_data)
    except requests.exceptions.ConnectionError:
        logger.debug(f"Door connection error at {config['ip']}")
        response_data = {
            'success': False,
            'status': 'offline',
            'online': False,
            'enabled': True,
            'device_name': config['device_name'],
            'message': 'Δεν βρέθηκε η συσκευή'
        }
        log_door_access(request, 'status', 'offline', response_data)
        return Response(response_data)
    except Exception as e:
        logger.error(f"Door status error: {e}")
        response_data = {
            'success': False,
            'status': 'error',
            'online': False,
            'enabled': True,
            'device_name': config['device_name'],
            'message': str(e)
        }
        log_door_access(request, 'status', 'failed', response_data)
        return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@throttle_classes([DoorActionThrottle])
def door_open(request):
    """
    Open/toggle the door via Tasmota relay.
    POST /api/v1/door/open/

    Requires: Staff/Admin user

    Returns:
        - success: bool
        - message: str (Greek)
        - new_status: "open" | "closed"
    """
    config = get_tasmota_config()

    # Check if enabled
    if not config['enabled']:
        return Response({
            'success': False,
            'message': 'Ο έλεγχος πόρτας είναι απενεργοποιημένος',
            'enabled': False
        }, status=400)

    try:
        # Toggle the relay
        url = f"{config['base_url']}/cm?cmnd=Power%20Toggle"

        logger.info(f"User {request.user.username} toggling door at {config['ip']}")
        response = requests.get(url, timeout=config['timeout'])

        if response.status_code == 200:
            data = response.json()
            new_power = data.get("POWER", "OFF")

            logger.info(f"Door toggled by {request.user.username}, new state: {new_power}")

            response_data = {
                'success': True,
                'message': 'Η πόρτα άνοιξε!' if new_power == 'ON' else 'Η πόρτα έκλεισε!',
                'new_status': 'open' if new_power == 'ON' else 'closed'
            }
            log_door_access(request, 'toggle', 'success', response_data)
            return Response(response_data)
        else:
            response_data = {
                'success': False,
                'message': 'Αποτυχία επικοινωνίας με τη συσκευή',
                'online': False
            }
            log_door_access(request, 'toggle', 'failed', response_data)
            return Response(response_data)

    except requests.exceptions.Timeout:
        logger.debug(f"Door toggle timeout for user {request.user.username}")
        response_data = {
            'success': False,
            'message': 'Timeout - η συσκευή δεν απαντά',
            'online': False
        }
        log_door_access(request, 'toggle', 'timeout', response_data)
        return Response(response_data)
    except requests.exceptions.ConnectionError:
        logger.debug(f"Door toggle connection error for user {request.user.username}")
        response_data = {
            'success': False,
            'message': 'Δεν βρέθηκε η συσκευή',
            'online': False
        }
        log_door_access(request, 'toggle', 'offline', response_data)
        return Response(response_data)
    except Exception as e:
        logger.error(f"Door toggle error for user {request.user.username}: {e}")
        response_data = {
            'success': False,
            'message': f'Σφάλμα: {str(e)}',
            'online': False
        }
        log_door_access(request, 'toggle', 'failed', response_data)
        return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@throttle_classes([DoorActionThrottle])
def door_pulse(request):
    """
    Pulse the door relay (momentary on for electric locks).
    POST /api/v1/door/pulse/

    Requires: Staff/Admin user

    Optional body:
        - duration: float (seconds, default 0.5)

    Returns:
        - success: bool
        - message: str (Greek)
    """
    config = get_tasmota_config()

    # Check if enabled
    if not config['enabled']:
        return Response({
            'success': False,
            'message': 'Ο έλεγχος πόρτας είναι απενεργοποιημένος',
            'enabled': False
        }, status=400)

    try:
        duration = float(request.data.get('duration', 0.5))

        # Security: limit max pulse duration to 5 seconds
        if duration > 5:
            return Response({
                'success': False,
                'message': 'Μέγιστη διάρκεια pulse: 5 δευτερόλεπτα'
            }, status=400)

        pulse_time = int(duration * 10)  # Tasmota uses deciseconds (0.1s units)

        # Set pulse time
        set_pulse_url = f"{config['base_url']}/cm?cmnd=PulseTime1%20{pulse_time}"
        requests.get(set_pulse_url, timeout=config['timeout'])

        # Trigger pulse
        pulse_url = f"{config['base_url']}/cm?cmnd=Power%20ON"

        logger.info(f"User {request.user.username} pulsing door for {duration}s")
        response = requests.get(pulse_url, timeout=config['timeout'])

        if response.status_code == 200:
            logger.info(f"Door pulsed by {request.user.username}")
            response_data = {
                'success': True,
                'message': f'Πόρτα ανοιχτή για {duration} δευτ.'
            }
            log_door_access(request, 'pulse', 'success', response_data)
            return Response(response_data)
        else:
            response_data = {
                'success': False,
                'message': 'Αποτυχία επικοινωνίας με τη συσκευή',
                'online': False
            }
            log_door_access(request, 'pulse', 'failed', response_data)
            return Response(response_data)

    except requests.exceptions.Timeout:
        response_data = {
            'success': False,
            'message': 'Timeout - η συσκευή δεν απαντά',
            'online': False
        }
        log_door_access(request, 'pulse', 'timeout', response_data)
        return Response(response_data)
    except requests.exceptions.ConnectionError:
        response_data = {
            'success': False,
            'message': 'Δεν βρέθηκε η συσκευή',
            'online': False
        }
        log_door_access(request, 'pulse', 'offline', response_data)
        return Response(response_data)
    except Exception as e:
        logger.error(f"Door pulse error: {e}")
        response_data = {
            'success': False,
            'message': f'Σφάλμα: {str(e)}',
            'online': False
        }
        log_door_access(request, 'pulse', 'failed', response_data)
        return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def door_access_logs(request):
    """
    Get recent door access logs.
    GET /api/v1/door/logs/

    Query params:
        - limit: int (default 50, max 200)
        - user_id: int (filter by user)
        - action: str (filter by action type)

    Returns list of recent door access entries.
    """
    from .models import DoorAccessLog

    limit = min(int(request.query_params.get('limit', 50)), 200)

    logs = DoorAccessLog.objects.select_related('user').all()

    # Optional filters
    user_id = request.query_params.get('user_id')
    if user_id:
        logs = logs.filter(user_id=user_id)

    action = request.query_params.get('action')
    if action:
        logs = logs.filter(action=action)

    logs = logs[:limit]

    return Response({
        'count': len(logs),
        'logs': [
            {
                'id': log.id,
                'user': log.user.username if log.user else None,
                'action': log.action,
                'action_display': log.get_action_display(),
                'result': log.result,
                'result_display': log.get_result_display(),
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat(),
            }
            for log in logs
        ]
    })
