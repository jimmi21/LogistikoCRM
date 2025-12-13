# ============================================================================
# D.P. Economy - Complete Setup Script
# One-command installation for Windows
# ============================================================================

param(
    [switch]$SkipGit,
    [switch]$UseDocker,
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " D.P. Economy - Complete Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/10] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Install from https://www.python.org" -ForegroundColor Red
    exit 1
}

# Check Git (optional)
if (-not $SkipGit) {
    Write-Host "[2/10] Checking Git..." -ForegroundColor Yellow
    try {
        $gitVersion = git --version 2>&1
        Write-Host "✅ $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Git not found - will skip Git operations" -ForegroundColor Yellow
        $SkipGit = $true
    }
}

# Create virtual environment
Write-Host "[3/10] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️ venv exists, removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}
python -m venv venv
Write-Host "✅ Virtual environment created" -ForegroundColor Green

# Activate venv
Write-Host "[4/10] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "[5/10] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "[6/10] Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray

# Try setup.cfg first
try {
    pip install -e . --quiet 2>&1 | Out-Null
    Write-Host "✅ Dependencies installed from setup.cfg" -ForegroundColor Green
} catch {
    Write-Host "⚠️ setup.cfg failed, trying requirements-complete.txt..." -ForegroundColor Yellow
    pip install -r requirements-complete.txt --quiet
    Write-Host "✅ Dependencies installed from requirements-complete.txt" -ForegroundColor Green
}

# Setup .env
Write-Host "[7/10] Configuring environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"

        # Generate SECRET_KEY
        $secretKey = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).Guid + (New-Guid).Guid))
        (Get-Content ".env") -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey" | Set-Content ".env"

        # Generate FRITZ_API_TOKEN
        $fritzToken = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).Guid))
        (Get-Content ".env") -replace "FRITZ_API_TOKEN=.*", "FRITZ_API_TOKEN=$fritzToken" | Set-Content ".env"

        Write-Host "✅ .env file created with secure tokens" -ForegroundColor Green
    } else {
        Write-Host "⚠️ .env.example not found!" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Run migrations
Write-Host "[8/10] Setting up database..." -ForegroundColor Yellow

# Check for migration conflicts
$conflictCheck = python manage.py migrate --check 2>&1 | Out-String
if ($conflictCheck -like "*Conflicting migrations*") {
    Write-Host "⚠️ Migration conflict detected, merging..." -ForegroundColor Yellow
    Write-Host "y" | python manage.py makemigrations --merge 2>&1 | Out-Null
}

python manage.py migrate --noinput
Write-Host "✅ Database setup complete" -ForegroundColor Green

# Create superuser (non-interactive)
Write-Host "[9/10] Creating admin user..." -ForegroundColor Yellow
$env:DJANGO_SUPERUSER_PASSWORD = "admin"
$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL = "admin@dpeconomy.local"

try {
    python manage.py createsuperuser --noinput 2>&1 | Out-Null
    Write-Host "✅ Admin user created (username: admin, password: admin)" -ForegroundColor Green
    Write-Host "⚠️  CHANGE PASSWORD AFTER LOGIN!" -ForegroundColor Yellow
} catch {
    Write-Host "⚠️ Admin user already exists or creation failed" -ForegroundColor Yellow
}

# Collect static files
Write-Host "[10/10] Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear 2>&1 | Out-Null
Write-Host "✅ Static files collected" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Complete! 🎉" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Activate venv:      venv\Scripts\activate" -ForegroundColor Gray
Write-Host "2. Start server:       python manage.py runserver" -ForegroundColor Gray
Write-Host "3. Open browser:       http://localhost:8000" -ForegroundColor Gray
Write-Host "4. Admin panel:        http://localhost:8000/admin" -ForegroundColor Gray
Write-Host "   Username: admin" -ForegroundColor Gray
Write-Host "   Password: admin (CHANGE THIS!)" -ForegroundColor Gray
Write-Host ""
Write-Host "Optional services:" -ForegroundColor White
Write-Host "- Fritz Monitor:       python fritz_monitor.py" -ForegroundColor Gray
Write-Host "- Celery worker:       celery -A webcrm worker -l info" -ForegroundColor Gray
Write-Host ""
