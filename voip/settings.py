

SECRET_ZADARMA_KEY = '123'
SECRET_ZADARMA = 'secret'
VOIP = [
    {
        'BACKEND': 'voip.backends.zadarmabackend.ZadarmaAPI',
        'PROVIDER': 'Zadarma',
        'IP': '185.45.152.42',
        'OPTIONS': {
            'key': SECRET_ZADARMA_KEY,
            'secret': SECRET_ZADARMA
        }
    }
]

VOIP_FORWARD_DATA = False
VOIP_FORWARDING_IP = ''


VOIP_FORWARD_URL = 'Url to forward'




EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Django-Q Configuration (NEW)
Q_CLUSTER = {
    'name': 'LogistikoCRM',
    # ... etc
}