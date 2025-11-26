# 📋 Production Deployment Checklist για LogistikoCRM
## Λογιστικό Γραφείο - Ready for Production

Αυτό το checklist διασφαλίζει ότι το σύστημα είναι έτοιμο για χρήση σε production environment.

---

## ✅ Pre-Deployment Checklist

### 1. **Testing** (ΚΡΙΤΙΚΟ)
- [ ] Τρέξε όλα τα tests: `python manage.py test`
- [ ] Verify test coverage: `coverage run manage.py test && coverage report`
- [ ] Όλα τα tests πρέπει να περνούν (100% success rate)
- [ ] Coverage πρέπει να είναι >70% για accounting, crm, inventory

**Test Command:**
```bash
python manage.py test tests.accounting tests.inventory tests.crm tests.common tests.integration --keepdb
```

---

### 2. **Database** (ΚΡΙΤΙΚΟ)
- [ ] Backup της τρέχουσας βάσης δεδομένων
- [ ] Run migrations: `python manage.py migrate`
- [ ] Check for pending migrations: `python manage.py showmigrations`
- [ ] Verify database integrity: `python manage.py check`

**Backup Command:**
```bash
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

---

### 3. **Email Configuration** (ΚΡΙΤΙΚΟ για Λογιστικό)
- [ ] Configure email settings στο `settings.py`:
  - `EMAIL_HOST` (π.χ. smtp.gmail.com)
  - `EMAIL_PORT` (π.χ. 587)
  - `EMAIL_USE_TLS` = True
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`
- [ ] Test email sending με test email
- [ ] Configure `DEFAULT_FROM_EMAIL`
- [ ] Setup email accounts στο Massmail app για κάθε accountant
- [ ] Mark one email account ως **main** για κάθε user

**Test Email:**
```python
from django.core.mail import send_mail
send_mail('Test', 'This is a test', 'from@example.com', ['to@example.com'])
```

---

### 4. **Accounting App Configuration** (ΚΡΙΤΙΚΟ)
- [ ] Create initial **ObligationType** records (ΦΠΑ, ΜΥΦ, κλπ)
- [ ] Create **ObligationProfile** packages (π.χ. Μισθοδοσία)
- [ ] Setup **EmailTemplate** για κάθε notification type:
  - Obligation completion
  - Deadline reminders
  - Overdue alerts
- [ ] Configure **EmailAutomationRule** για auto-notifications
- [ ] Test `generate_monthly_obligations` command

**Setup Commands:**
```bash
# Test obligation generation
python manage.py generate_monthly_obligations --month 12 --year 2024 --dry-run
```

---

### 5. **User & Permissions Setup**
- [ ] Create admin superuser
- [ ] Create user groups:
  - `co-workers` (auto-assigned)
  - `accountants`
  - `chiefs`
  - `managers`
  - `operators`
- [ ] Assign users to appropriate groups
- [ ] Test permissions για κάθε role
- [ ] Verify UserProfile auto-creation signal

**Create Superuser:**
```bash
python manage.py createsuperuser
```

---

### 6. **Media & Static Files**
- [ ] Configure `MEDIA_ROOT` και `MEDIA_URL`
- [ ] Configure `STATIC_ROOT` και `STATIC_URL`
- [ ] Run `python manage.py collectstatic`
- [ ] Verify folder permissions (writable by Django)
- [ ] Test file uploads (ClientDocument)
- [ ] Verify client folder auto-creation works

**Static Files:**
```bash
python manage.py collectstatic --noinput
```

---

### 7. **Security Settings** (ΚΡΙΤΙΚΟ)
- [ ] Set `DEBUG = False` στο production
- [ ] Set `ALLOWED_HOSTS` με το production domain
- [ ] Configure `SECRET_KEY` (unique, secure)
- [ ] Setup HTTPS/SSL certificate
- [ ] Configure `SECURE_SSL_REDIRECT = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Configure `X_FRAME_OPTIONS = 'DENY'`

**Security Check:**
```bash
python manage.py check --deploy
```

---

### 8. **Cron Jobs / Scheduled Tasks** (ΚΡΙΤΙΚΟ)
Setup τα παρακάτω scheduled tasks:

#### **Daily Tasks:**
```bash
# Generate next month's obligations (1st of month)
0 0 1 * * cd /path/to/app && python manage.py generate_monthly_obligations

# Send daily obligations report
0 8 * * * cd /path/to/app && python manage.py send_daily_obligations_report --send-email

# Backup database
0 2 * * * cd /path/to/app && python manage.py backup_database
```

#### **Weekly Tasks:**
```bash
# Clean old data (optional)
0 3 * * 0 cd /path/to/app && python manage.py clean_duplicates
```

---

### 9. **Monitoring & Logging**
- [ ] Configure logging στο `settings.py`
- [ ] Setup log rotation
- [ ] Configure error email notifications (ADMINS setting)
- [ ] Test error logging
- [ ] Setup monitoring για:
  - Database connections
  - Email sending failures
  - Disk space (MEDIA folder)

**Logging Configuration:**
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/logistikocrm/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'accounting': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

### 10. **Initial Data Setup**
- [ ] Import existing clients: `python manage.py import_clients clients.xlsx`
- [ ] Setup obligation types (ΦΠΑ, ΜΥΦ, Μισθοδοσία, κλπ)
- [ ] Create email templates
- [ ] Configure automation rules
- [ ] Test monthly obligation generation

---

## 🚀 Deployment Steps

### Step 1: Prepare Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=settings.production
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/db"
```

### Step 2: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup initial data
python manage.py setupdata  # If available
```

### Step 3: Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Test static file serving
curl http://localhost/static/admin/css/base.css
```

### Step 4: Test Critical Functions
```bash
# Test obligation generation
python manage.py generate_monthly_obligations --dry-run

# Test email sending
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test', 'from@example.com', ['to@example.com'])
```

### Step 5: Start Server
```bash
# Using Gunicorn (recommended)
gunicorn settings.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Or using Django dev server (ONLY for testing)
python manage.py runserver 0.0.0.0:8000
```

---

## ✅ Post-Deployment Verification

### Immediate Checks (Κάνε μόλις deploy)
- [ ] Login ως admin
- [ ] Create test client
- [ ] Verify folder structure created
- [ ] Add test obligation to client
- [ ] Generate monthly obligations για επόμενο μήνα
- [ ] Verify obligations created correctly
- [ ] Test email sending από CRM
- [ ] Test file upload (ClientDocument)
- [ ] Check all pages load without errors
- [ ] Verify timezone settings

### First Week Monitoring
- [ ] Monitor logs for errors
- [ ] Check email delivery rates
- [ ] Verify cron jobs running
- [ ] Monitor database size growth
- [ ] Check backup creation
- [ ] User feedback collection

### Monthly Tasks
- [ ] Review generated obligations
- [ ] Check overdue obligations
- [ ] Backup verification
- [ ] Performance review
- [ ] Security updates

---

## 📞 Support & Troubleshooting

### Common Issues

#### **Emails not sending:**
1. Check EMAIL_HOST_USER credentials
2. Verify firewall allows SMTP (port 587/465)
3. Check EmailAccount has `main=True`
4. Review email logs

#### **Obligations not generating:**
1. Verify ClientObligation.is_active = True
2. Check obligation_types assigned
3. Verify applicable_months for quarterly
4. Check cron job logs

#### **File upload errors:**
1. Check MEDIA_ROOT permissions
2. Verify folder_path exists
3. Check disk space

---

## 🔒 Security Best Practices

### Regular Maintenance
- [ ] Update Django monthly: `pip install --upgrade django`
- [ ] Review security advisories
- [ ] Rotate SECRET_KEY annually
- [ ] Review user permissions quarterly
- [ ] Check backup integrity monthly

### Access Control
- [ ] Use strong passwords
- [ ] Enable 2FA for admin accounts
- [ ] Limit admin access by IP (if possible)
- [ ] Regular password rotation
- [ ] Audit user activity logs

---

## 📊 Performance Optimization

### Database
- [ ] Create indexes για frequently queried fields
- [ ] Regular VACUUM (PostgreSQL)
- [ ] Monitor slow queries
- [ ] Configure connection pooling

### Caching (Optional)
- [ ] Setup Redis/Memcached
- [ ] Cache obligation listings
- [ ] Cache dashboard statistics

---

## 🎯 Success Criteria

Το σύστημα είναι production-ready όταν:

✅ **Όλα τα tests περνούν** (100% success)
✅ **Test coverage >70%** για accounting, crm
✅ **Email sending λειτουργεί** (test με πραγματικό email)
✅ **Monthly obligations δημιουργούνται αυτόματα**
✅ **File uploads λειτουργούν**
✅ **Backups τρέχουν αυτόματα**
✅ **Logging configured και λειτουργεί**
✅ **Security checks passed** (`manage.py check --deploy`)
✅ **No critical errors in logs** για 48 ώρες

---

## 📞 Emergency Contacts

**Critical Issues:**
- Database failure → Restore from backup
- Email failure → Check SMTP credentials
- Server crash → Check logs, restart server
- Data corruption → Restore from last good backup

**Backup Locations:**
- Daily: `/backups/daily/`
- Weekly: `/backups/weekly/`
- Monthly: `/backups/monthly/`

---

## 🎉 Ready for Production!

Μόλις ολοκληρώσεις αυτό το checklist, το σύστημα είναι έτοιμο να χρησιμοποιηθεί στο λογιστικό σου γραφείο με ασφάλεια και σιγουριά!

**Καλή επιτυχία! 🚀**
