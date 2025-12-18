"""
Local/Production Settings Override
"""
from .settings import *
import os

# Determine environment
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    DEBUG = False
    # Πρόσθεσε τις IPs που χρειάζεσαι
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

    # Security για production
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 86400  # 24 hours

else:  # development
    DEBUG = True
    # Δέχεται όλες τις IPs για εύκολο local development
    ALLOWED_HOSTS = ['*']

    # IMPORTANT: Reset production security settings for development
    # These may have been set in settings.py's "if not DEBUG:" block
    # before this file had a chance to set DEBUG = True
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Allow all CORS origins in development
    CORS_ALLOW_ALL_ORIGINS = True

# Αυτόματη ανίχνευση τοπικής IP για CSRF
def get_local_ip():
    """Βρίσκει την τοπική IP του server"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

LOCAL_IP = get_local_ip()

# CSRF για local network - αυτόματη ρύθμιση
CSRF_TRUSTED_ORIGINS = [
    f'http://{LOCAL_IP}:8000',
    f'http://{LOCAL_IP}:3000',
    'http://localhost:8000',
    'http://localhost:3000',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000',
]

# Improved Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounting': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if not exists
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)