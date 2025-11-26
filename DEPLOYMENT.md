# 🚀 LogistikoCRM - Production Deployment Guide

Complete deployment guide for accounting office (Λογιστικό Γραφείο)

## Prerequisites

- Ubuntu 20.04+ / Debian 11+
- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (for Celery)
- Nginx
- Supervisor

## Installation Steps

### 1. System Dependencies

```bash
sudo apt update && sudo apt install -y     python3.10 python3-pip python3-venv     postgresql redis-server nginx supervisor     libpq-dev libmagic1
```

### 2. Clone & Setup

```bash
cd /var/www
git clone <repo-url> LogistikoCRM
cd LogistikoCRM
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Fill in production values
```

### 4. Database Setup

```bash
sudo -u postgres createdb logistikocrm
sudo -u postgres createuser logistikocrm_user
python manage.py migrate
python manage.py createsuperuser
```

### 5. Static Files

```bash
python manage.py collectstatic --noinput
```

## Security Checklist

- [x] DEBUG=False
- [x] Strong SECRET_KEY
- [x] All passwords in .env
- [x] CSRF protection enabled
- [x] XSS protection in place
- [x] File upload validation
- [x] Audit trail active

## Backup Configuration

```bash
# Daily backup at 2 AM
crontab -e
0 2 * * * /var/www/LogistikoCRM/scripts/backup_cron.sh
```

## Support

For issues, contact system administrator.
