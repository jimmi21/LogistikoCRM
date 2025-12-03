# Zadarma VoIP Configuration
# Override these values via environment variables or settings_local.py
import os

SECRET_ZADARMA_KEY = os.environ.get('ZADARMA_KEY', '')
SECRET_ZADARMA = os.environ.get('ZADARMA_SECRET', '')

VOIP = [
    {
        'BACKEND': 'voip.backends.zadarmabackend.ZadarmaAPI',
        'PROVIDER': 'Zadarma',
        'IP': '185.45.152.42',  # Zadarma webhook source IP
        'OPTIONS': {
            'key': SECRET_ZADARMA_KEY,
            'secret': SECRET_ZADARMA
        }
    }
]

# Forward unmatched calls to another CRM instance (e.g., subsidiary)
VOIP_FORWARD_DATA = False
VOIP_FORWARDING_IP = os.environ.get('VOIP_FORWARDING_IP', '')
VOIP_FORWARD_URL = os.environ.get('VOIP_FORWARD_URL', '')