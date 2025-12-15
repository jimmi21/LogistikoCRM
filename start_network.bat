@echo off
REM Script για εκκίνηση LogistikoCRM στο τοπικό δίκτυο (Windows)
REM Χρήση: start_network.bat

echo.
echo 🚀 Εκκίνηση LogistikoCRM για τοπικό δίκτυο...
echo.

REM Εύρεση τοπικού IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP:~1%

echo 📊 Πληροφορίες Δικτύου:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🌐 Τοπικό IP: %LOCAL_IP%
echo.
echo 📱 Οι άλλοι χρήστες μπορούν να συνδεθούν από:
echo    http://%LOCAL_IP%:8000
echo    http://%LOCAL_IP%:8000/admin
echo.
echo 💡 Σημείωση: Βεβαιώσου ότι το firewall επιτρέπει το port 8000
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Ενεργοποίηση virtual environment (αν υπάρχει)
if exist venv\Scripts\activate.bat (
    echo 📦 Ενεργοποίηση virtual environment...
    call venv\Scripts\activate.bat
)

REM Εκκίνηση Django server
echo 🔥 Εκκίνηση Django server στο 0.0.0.0:8000...
echo    Πάτησε Ctrl+C για τερματισμό
echo.

python manage.py runserver 0.0.0.0:8000

pause
