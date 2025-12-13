# 🚀 D.P. Economy - Installation Guide

Quick installation guide for D.P. Economy CRM system.

---

## 📋 Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads)) - Optional
- **Node.js 18+** ([Download](https://nodejs.org/)) - Optional, for frontend

---

## ⚡ Quick Start (3 Options)

### **Option 1: One-Command Setup** ⭐ RECOMMENDED

```powershell
# Run automated setup script
.\setup-complete.ps1

# That's it! Server ready at http://localhost:8000
```

---

### **Option 2: Docker** 🐳 PRODUCTION READY

```powershell
# Start all services
docker-compose up -d

# Access at http://localhost:8000
# Admin: username=admin, password=admin
```

---

### **Option 3: Manual Installation**

```powershell
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Setup environment
copy .env.example .env
# Edit .env with your settings

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

---

## 🎯 Post-Installation

### Access Points

- **Main App:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/api/schema/swagger-ui/

### Default Credentials (Change immediately!)

- **Username:** admin
- **Password:** admin

### Optional Services

```powershell
# Fritz!Box VoIP Monitor
python fritz_monitor.py

# Celery Worker (background tasks)
celery -A webcrm worker -l info

# Celery Beat (scheduled tasks)
celery -A webcrm beat -l info
```

---

## 🔧 Configuration

### Environment Variables (.env)

Key variables to configure:

```bash
# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Fritz!Box VoIP
FRITZ_API_TOKEN=your-secure-token
```

### Generate Secure Tokens

```powershell
# SECRET_KEY
$key = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).Guid + (New-Guid).Guid))
Write-Host "SECRET_KEY=$key"

# FRITZ_API_TOKEN
$token = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).Guid))
Write-Host "FRITZ_API_TOKEN=$token"
```

---

## 🐛 Troubleshooting

### Migration Conflicts

```powershell
python manage.py makemigrations --merge
python manage.py migrate
```

### Missing Packages

```powershell
pip install -r requirements-complete.txt
```

### Database Reset

```powershell
# Delete database
del db.sqlite3

# Recreate
python manage.py migrate
python manage.py createsuperuser
```

---

## 📚 Documentation

- [CLAUDE.md](CLAUDE.md) - Developer guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) - Pre-launch checklist

---

## 💡 Tips

1. **Use Docker** for easiest setup
2. **Run setup-complete.ps1** for automated installation
3. **Change default passwords** immediately
4. **Configure .env** before production use
5. **Enable Fritz!Box CallMonitor** with `#96*5*`

---

## 🆘 Support

If you encounter issues:

1. Check [Troubleshooting](#-troubleshooting) section
2. Review error messages carefully
3. Ensure all prerequisites are installed
4. Verify .env configuration

---

**Last Updated:** December 2025
**Version:** 1.5.2
