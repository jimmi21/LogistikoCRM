# accounting/tasmota_control.py
"""
Tasmota Device Control για πόρτα γραφείου
"""

import requests
from django.conf import settings
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
import logging

logger = logging.getLogger(__name__)

# SECURITY FIX: Tasmota Configuration loaded from Django settings
TASMOTA_CONFIG = {
    'door': {
        'ip': settings.TASMOTA_IP,  # Loaded from environment variables via settings
        'name': settings.TASMOTA_DEVICE_NAME,
        'relay': 'POWER',  # ή POWER αν έχει 1 relay
        'pulse_time': 1,  # 1 δευτερόλεπτο pulse για ηλεκτρική κλειδαριά
    }
}

class TasmotaController:
    """Controller για Tasmota devices"""
    
    @staticmethod
    def send_command(device_name, command):
        """Στέλνει εντολή στο Tasmota"""
        try:
            device = TASMOTA_CONFIG.get(device_name)
            if not device:
                return {'success': False, 'error': 'Device not found'}
            
            url = f"http://{device['ip']}/cm?cmnd={command}"
            
            response = requests.get(url, timeout=5)
            data = response.json()
            
            logger.info(f"Tasmota command sent: {command} to {device_name}")
            logger.info(f"Response: {data}")
            
            return {
                'success': True,
                'device': device_name,
                'command': command,
                'response': data
            }
            
        except requests.RequestException as e:
            logger.error(f"Tasmota error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def toggle_door():
        """Toggle πόρτα (pulse για ηλεκτρική κλειδαριά)"""
        # PulseTime1 10 = 1 second pulse
        result = TasmotaController.send_command('door', 'Pulse1')
        return result
    
    @staticmethod
    def get_door_status():
        """Παίρνει status της πόρτας"""
        result = TasmotaController.send_command('door', 'Status')
        if result['success']:
            status = result['response'].get('Status', {}).get('Power', 0)
            result['is_open'] = status == 1
        return result
    
    @staticmethod
    def unlock_door(duration=1):
        """Ξεκλειδώνει την πόρτα για X δευτερόλεπτα"""
        # Ρυθμίζει pulse time
        TasmotaController.send_command('door', f'PulseTime1 {duration * 10}')
        # Ενεργοποιεί το pulse
        result = TasmotaController.send_command('door', 'POWER1 ON')
        return result


# Views για AJAX calls

@staff_member_required
def door_control(request):
    """AJAX endpoint για door control"""
    action = request.POST.get('action', request.GET.get('action'))
    
    if action == 'unlock':
        duration = int(request.POST.get('duration', 1))
        result = TasmotaController.unlock_door(duration)
    elif action == 'status':
        result = TasmotaController.get_door_status()
    elif action == 'toggle':
        result = TasmotaController.toggle_door()
    else:
        result = {'success': False, 'error': 'Invalid action'}
    
    return JsonResponse(result)


@staff_member_required
def door_control_widget(request):
    """Render door control widget"""
    from django.shortcuts import render
    
    # Get current status
    status = TasmotaController.get_door_status()
    
    context = {
        'device_online': status['success'],
        'door_status': status.get('is_open', False),
        'device_ip': TASMOTA_CONFIG['door']['ip'],
    }
    
    return render(request, 'accounting/door_widget.html', context)