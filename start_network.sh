#!/bin/bash
# Script για εκκίνηση LogistikoCRM στο τοπικό δίκτυο
# Χρήση: ./start_network.sh

echo "🚀 Εκκίνηση LogistikoCRM για τοπικό δίκτυο..."
echo ""

# Εύρεση τοπικού IP
if command -v ip &> /dev/null; then
    # Linux
    LOCAL_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
elif command -v ipconfig &> /dev/null; then
    # Windows (Git Bash)
    LOCAL_IP=$(ipconfig | grep -oP '(?<=IPv4 Address[. ]*: )\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
else
    LOCAL_IP="<το-IP-σας>"
fi

# Έλεγχος αν το DEBUG είναι ενεργό
if grep -q "DEBUG.*=.*True" webcrm/settings.py || grep -q "DEBUG.*=.*'True'" .env 2>/dev/null; then
    DEBUG_STATUS="✅ Ενεργό"
else
    DEBUG_STATUS="⚠️  Ανενεργό (πρέπει να το ενεργοποιήσεις στο .env)"
fi

echo "📊 Πληροφορίες Δικτύου:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Τοπικό IP: $LOCAL_IP"
echo "🔧 DEBUG Mode: $DEBUG_STATUS"
echo ""
echo "📱 Οι άλλοι χρήστες μπορούν να συνδεθούν από:"
echo "   http://$LOCAL_IP:8000"
echo "   http://$LOCAL_IP:8000/admin"
echo ""
echo "💡 Σημείωση: Βεβαιώσου ότι το firewall επιτρέπει το port 8000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ενεργοποίηση virtual environment (αν υπάρχει)
if [ -d "venv" ]; then
    echo "📦 Ενεργοποίηση virtual environment..."
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
fi

# Εκκίνηση Django server
echo "🔥 Εκκίνηση Django server στο 0.0.0.0:8000..."
echo "   Πάτησε Ctrl+C για τερματισμό"
echo ""

python manage.py runserver 0.0.0.0:8000
