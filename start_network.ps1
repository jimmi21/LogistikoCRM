# PowerShell Script - Εκκίνηση Django για Τοπικό Δίκτυο (Windows)
# Χρήση: .\start_network.ps1

Write-Host ""
Write-Host "🚀 Εκκίνηση LogistikoCRM για τοπικό δίκτυο..." -ForegroundColor Green
Write-Host ""

# Βρες το τοπικό IP
$LocalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Select-Object -First 1).IPAddress

Write-Host "📊 Πληροφορίες Δικτύου:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🌐 Τοπικό IP: $LocalIP" -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 Οι άλλοι χρήστες μπορούν να συνδεθούν από:" -ForegroundColor White
Write-Host "   http://${LocalIP}:8000" -ForegroundColor Green
Write-Host "   http://${LocalIP}:8000/admin" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Σημείωση: Βεβαιώσου ότι το firewall επιτρέπει το port 8000" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Έλεγχος .env
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  Δεν βρέθηκε .env file. Δημιουργία..." -ForegroundColor Yellow
    @"
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
DB_ENGINE=django.db.backends.sqlite3
EMAIL_BACKEND_CONSOLE=true
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "✅ .env δημιουργήθηκε" -ForegroundColor Green
} else {
    Write-Host "✅ .env βρέθηκε" -ForegroundColor Green
}

# Έλεγχος virtual environment
if (-Not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment δεν βρέθηκε. Δημιουργία..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment δημιουργήθηκε" -ForegroundColor Green
}

# Ενεργοποίηση venv
Write-Host "📦 Ενεργοποίηση virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Εκκίνηση Django server
Write-Host ""
Write-Host "🔥 Εκκίνηση Django server στο 0.0.0.0:8000..." -ForegroundColor Green
Write-Host "   Πάτησε Ctrl+C για τερματισμό" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 0.0.0.0:8000
