# CLAUDE.md - LogistikoCRM AI Assistant Guide

## Project Overview

**LogistikoCRM** is a production-ready Django-based CRM system tailored for Greek accounting offices (Λογιστικό Γραφείο). It's built on top of the open-source Django-CRM project with specialized accounting and tax compliance features.

**Key characteristics:**
- Enterprise-grade CRM with Greek tax (myDATA) integration
- Django 5.x backend with React.js frontend option
- PostgreSQL/MySQL for production, SQLite for development
- Multi-language support (23 languages, Greek default)
- Timezone: Europe/Athens

## Technology Stack

### Backend
- **Framework:** Django 5.0-5.2 (LTS)
- **Database:** PostgreSQL 14+ (production), SQLite (development)
- **API:** Django REST Framework 3.14+ with JWT authentication
- **Task Queue:** Celery 5.3+ with Redis, Django-Q (database-backed alternative)
- **WSGI Server:** Gunicorn 21.2+

### Frontend
- **Framework:** React 19.2 (in `/frontend/`)
- **Styling:** Tailwind CSS 4.1+
- **Charts:** Recharts 3.2+
- **HTTP Client:** Axios 1.12+

### Key Dependencies
```
Django>=5.0,<5.1
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0
celery>=5.3.4
redis>=5.0.1
openpyxl>=3.1.2
Pillow>=10.1.0
python-magic>=0.4.27
gunicorn>=21.2.0
```

## Directory Structure

```
LogistikoCRM/
├── accounting/          # Greek accounting office features (ClientProfile, Obligations)
├── analytics/           # Reports & dashboards (IncomeStat, RequestStat, etc.)
├── chat/                # Internal messaging system
├── common/              # Shared utilities (UserProfile, Reminder, Tag, File, AuditLog)
├── crm/                 # Core CRM (Request, Deal, Lead, Company, Contact, Payment)
├── crm-frontend/        # Alternative frontend
├── docs/                # Documentation (MkDocs)
├── frontend/            # React.js frontend application
├── help/                # Context-sensitive help system
├── inventory/           # Inventory management with myDATA compliance
├── locale/              # i18n translations (23 languages)
├── massmail/            # Email marketing & campaigns
├── media/               # User-uploaded files (runtime)
├── mydata/              # Greek myDATA tax authority API integration
├── scripts/             # Automation scripts (backup, etc.)
├── settings/            # CRM configuration module
├── static/              # Static assets (CSS, JS, images)
├── tasks/               # Task & project management
├── templates/           # Django HTML templates
├── tests/               # Test suites (pytest-django)
├── voip/                # VoIP & telephony integration
├── webcrm/              # Django project configuration
│   ├── settings.py      # Main Django settings
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI application
│   ├── celery.py        # Celery configuration
│   └── datetime_settings.py
└── .github/             # GitHub workflows & templates
```

## Development Setup

### Prerequisites
```bash
# System dependencies (Debian/Ubuntu)
sudo apt-get install python3.10+ libpq-dev python3-dev libmagic1

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
```bash
SECRET_KEY=your-random-secret-key
DEBUG=True  # False in production
DB_ENGINE=django.db.backends.sqlite3  # or postgresql
DB_NAME=db.sqlite3
EMAIL_HOST_PASSWORD=your-email-app-password
```

### Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### Frontend Development (React)
```bash
cd frontend
npm install
npm start        # Development server at :3000
npm run build    # Production build
```

## Testing

### Run All Tests
```bash
python manage.py test tests/ --noinput
```

### Run Specific App Tests
```bash
python manage.py test tests.accounting tests.inventory tests.crm --keepdb
```

### With pytest (preferred)
```bash
pytest tests/
pytest tests/accounting/ -v
pytest tests/ --cov=accounting --cov-report=html
```

### Test Structure
```
tests/
├── accounting/          # Accounting models, email service, commands
├── analytics/           # Analytics tests
├── chat/                # Chat tests
├── common/              # Common utilities, middleware, signals
├── crm/                 # CRM models, views, utils
├── help/                # Help system tests
├── integration/         # Integration tests (workflows)
├── inventory/           # Inventory tests
├── massmail/            # Email marketing tests
├── tasks/               # Task management tests
├── fixtures/            # Test data
├── utils/               # Test helpers
└── base_test_classes.py # Base test classes
```

## Code Conventions

### Python Style
- Follow PEP 8 guidelines
- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 .`
- Use `isort` for import sorting: `isort .`

### Django Patterns
- Models in `app/models.py` or `app/models/` directory
- Views in `app/views.py` or `app/views/` directory
- Admin customization in `app/admin.py`
- Forms in `app/forms.py`
- Serializers in `app/serializers.py`
- Management commands in `app/management/commands/`

### Naming Conventions
- Models: PascalCase (e.g., `ClientProfile`, `MonthlyObligation`)
- Views: snake_case functions or PascalCase for class-based views
- URLs: kebab-case (e.g., `/api/client-profiles/`)
- Templates: snake_case (e.g., `client_profile_list.html`)

### Greek-Specific Considerations
- VAT (ΦΠΑ) rate: 24% (configurable in settings: `VAT = 24`)
- Tax ID field: `afm` (9-digit Greek Tax ID)
- Tax office field: `doy` (Greek tax office name)
- Date formats: European style (DD/MM/YYYY)
- Currency: EUR (€)

## Key Configuration Files

### webcrm/settings.py
Main Django settings. Key sections:
- Lines 40-53: Database configuration (use env vars)
- Lines 120-146: INSTALLED_APPS
- Lines 344-354: REST Framework config
- Lines 358-361: JWT token lifetimes
- Lines 369-380: Django-Q cluster config
- Lines 444-464: Celery configuration

### Important Settings
```python
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
LANGUAGE_CODE = 'el'  # Greek default
TIME_ZONE = 'Europe/Athens'
VAT = 24  # Greek VAT rate
```

## Database Schema Highlights

### Core Models

**accounting.ClientProfile** - Extended client data for tax purposes:
- `afm` - Greek Tax ID (9 digits)
- `doy` - Tax office
- `taxpayer_type` - individual/professional/company
- `book_category` - tax book category
- Multiple addresses (home/business)
- Bank info (IBAN, etc.)

**accounting.MonthlyObligation** - Tax/social security deadlines:
- `client` - FK to ClientProfile
- `obligation_type` - FK to ObligationType
- `month`, `year` - Period
- `deadline` - Due date
- `status` - pending/submitted/paid/overdue

**crm.Request** - Commercial inquiries
**crm.Deal** - Sales opportunities
**crm.Lead** - Potential customers
**crm.Company** - Business entities
**crm.Contact** - Person contacts

**inventory.Invoice** - myDATA compliant invoices
**inventory.Product** - Goods/services catalog

## API Structure

### Authentication
- JWT tokens via `/api/token/` and `/api/token/refresh/`
- Session authentication for admin interface
- Access token lifetime: 5 hours
- Refresh token lifetime: 1 day

### CORS Configuration
Allowed origins for development:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

### Pagination
Default: 50 items per page

## Common Tasks

### Create Database Backup
```bash
python manage.py backup_database
# Or use script:
./scripts/backup_cron.sh
```

### Run Celery Workers
```bash
celery -A webcrm worker -l info
celery -A webcrm beat -l info  # For scheduled tasks
```

### Run Django-Q Workers (Alternative)
```bash
python manage.py qcluster
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Create Translations
```bash
python manage.py makemessages -l el  # Greek
python manage.py compilemessages
```

### Production Deployment Check
```bash
python manage.py check --deploy
```

## Security Considerations

### File Upload Validation
Files are validated in `common/utils/file_validation.py`:
- Whitelist extensions only
- MIME type verification via `python-magic`
- Size limits enforced

### Environment Variables
Never commit secrets. Use `.env` file for:
- `SECRET_KEY`
- `DB_PASSWORD`
- `EMAIL_HOST_PASSWORD`
- `MYDATA_SUBSCRIPTION_KEY`

### Production Settings
For production, ensure:
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

## Scheduled Tasks

### Celery Beat Schedule
- `send_obligation_reminders` - 09:00 Mon-Fri
- `send_daily_summary` - 17:00 Mon-Fri

### Django-Q Alternative
Uses database-backed queue (no Redis required):
- 2 workers
- 90-second timeout
- 50-item queue limit

## URLs Structure

Admin URLs use secret prefixes (configurable in settings):
- CRM: `/{SECRET_CRM_PREFIX}/`
- Admin: `/{SECRET_ADMIN_PREFIX}/`
- Login: `/{SECRET_LOGIN_PREFIX}/`

Default values: `123/`, `456-admin/`, `789-login/`

## Useful Commands

```bash
# Development server
python manage.py runserver 0.0.0.0:8000

# Shell with enhanced features
python manage.py shell_plus  # Requires django-extensions

# Create migrations
python manage.py makemigrations accounting inventory crm

# Apply migrations
python manage.py migrate

# Load initial data
python manage.py loaddata tests/fixtures/*.json

# Export data
python manage.py dumpdata accounting --indent 2 > backup.json
```

## Troubleshooting

### Common Issues

**1. Missing python-magic library:**
```bash
# Linux
sudo apt-get install libmagic1

# macOS
brew install libmagic
```

**2. PostgreSQL connection issues:**
```bash
# Ensure psycopg2 is installed
pip install psycopg2-binary
```

**3. Static files not loading:**
```bash
python manage.py collectstatic --noinput
# Ensure STATIC_ROOT is set correctly
```

**4. Celery tasks not running:**
```bash
# Check Redis is running
redis-cli ping
# Or use Django-Q (database-backed)
python manage.py qcluster
```

## Documentation Resources

- **User Guide:** `/docs/django-crm_user_guide.md`
- **Installation:** `/docs/installation_and_configuration_guide.md`
- **System Overview:** `/docs/crm_system_overview.md`
- **Task Features:** `/docs/django-crm_task_features.md`
- **Analytics:** `/docs/django-crm_analytics_app_overview.md`
- **ReadTheDocs:** https://django-crm-admin.readthedocs.io

## License

AGPL-3.0 - See LICENSE file for details.
