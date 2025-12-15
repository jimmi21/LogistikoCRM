#!/bin/bash
# Εκκίνηση Django + React Development Servers
# Χρήση: ./start_dev.sh

set -e

echo "🚀 Εκκίνηση LogistikoCRM Development Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Χρώματα για output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Βρες το τοπικό IP
if command -v ip &> /dev/null; then
    LOCAL_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
elif command -v ipconfig &> /dev/null; then
    LOCAL_IP=$(ipconfig | grep -oP '(?<=IPv4 Address[. ]*: )\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
else
    LOCAL_IP="<το-IP-σας>"
fi

# Έλεγχος .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Δεν βρέθηκε .env file. Δημιουργία...${NC}"
    cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
DB_ENGINE=django.db.backends.sqlite3
EMAIL_BACKEND_CONSOLE=true
EOF
    echo -e "${GREEN}✅ .env δημιουργήθηκε${NC}"
else
    echo -e "${GREEN}✅ .env βρέθηκε${NC}"
fi

# Έλεγχος virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment δεν βρέθηκε. Δημιουργία...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment δημιουργήθηκε${NC}"
fi

# Ενεργοποίηση venv
echo -e "${BLUE}📦 Ενεργοποίηση virtual environment...${NC}"
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Έλεγχος dependencies
if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies δεν είναι εγκατεστημένα. Εγκατάσταση...${NC}"
    pip install -r requirements.txt
fi

# Έλεγχος migrations
echo -e "${BLUE}🔍 Έλεγχος database migrations...${NC}"
python manage.py migrate --check &>/dev/null || {
    echo -e "${YELLOW}⚠️  Εκτέλεση migrations...${NC}"
    python manage.py migrate
}

# Έλεγχος frontend dependencies
if [ -d "frontend" ]; then
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${YELLOW}⚠️  Frontend dependencies δεν είναι εγκατεστημένα. Εγκατάσταση...${NC}"
        cd frontend
        npm install
        cd ..
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Έτοιμο για εκκίνηση!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📊 Πληροφορίες Σύνδεσης:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Django Backend:${NC}"
echo "   • http://localhost:8000"
echo "   • http://$LOCAL_IP:8000"
echo "   • http://localhost:8000/admin (Django Admin)"
echo ""
echo -e "${BLUE}React Frontend:${NC}"
echo "   • http://localhost:3000 (ή όπως δείχνει το Vite)"
echo "   • http://$LOCAL_IP:3000"
echo ""
echo -e "${YELLOW}⚠️  ΣΗΜΑΝΤΙΚΟ: Απενεργοποίησε Ad Blockers!${NC}"
echo "   uBlock Origin, AdBlock, Privacy Badger, κλπ."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Δημιουργία tmux session με 2 panes (αν υπάρχει tmux)
if command -v tmux &> /dev/null; then
    echo -e "${BLUE}🖥️  Εκκίνηση σε tmux session...${NC}"
    echo ""

    # Kill existing session if exists
    tmux kill-session -t logistikocrm 2>/dev/null || true

    # Create new session
    tmux new-session -d -s logistikocrm -n dev

    # Split window vertically
    tmux split-window -h -t logistikocrm:dev

    # Left pane: Django
    tmux send-keys -t logistikocrm:dev.0 "source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null" C-m
    tmux send-keys -t logistikocrm:dev.0 "echo '🐍 Django Backend'" C-m
    tmux send-keys -t logistikocrm:dev.0 "python manage.py runserver 0.0.0.0:8000" C-m

    # Right pane: React (με delay για να προλάβει το Django)
    tmux send-keys -t logistikocrm:dev.1 "sleep 3" C-m
    tmux send-keys -t logistikocrm:dev.1 "cd frontend" C-m
    tmux send-keys -t logistikocrm:dev.1 "echo '⚛️  React Frontend'" C-m
    tmux send-keys -t logistikocrm:dev.1 "npm start" C-m

    # Attach to session
    echo -e "${GREEN}✅ Servers ξεκίνησαν στο tmux session 'logistikocrm'${NC}"
    echo ""
    echo -e "${BLUE}Χρήσιμες εντολές:${NC}"
    echo "  • Ctrl+B, % : Διαχωρισμός pane"
    echo "  • Ctrl+B, ← → : Μετακίνηση μεταξύ panes"
    echo "  • Ctrl+B, D : Detach (servers συνεχίζουν στο background)"
    echo "  • tmux attach -t logistikocrm : Επανασύνδεση"
    echo "  • Ctrl+C (σε κάθε pane) : Τερματισμός servers"
    echo ""

    tmux attach -t logistikocrm

else
    # Χωρίς tmux - εκτέλεση παράλληλα με background processes
    echo -e "${YELLOW}⚠️  tmux δεν βρέθηκε. Εκκίνηση σε background...${NC}"
    echo ""

    # Start Django in background
    echo -e "${BLUE}🐍 Εκκίνηση Django backend...${NC}"
    python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
    DJANGO_PID=$!
    echo "   PID: $DJANGO_PID"

    # Wait a bit for Django to start
    sleep 3

    # Start React in background
    echo -e "${BLUE}⚛️  Εκκίνηση React frontend...${NC}"
    cd frontend
    npm start > ../react.log 2>&1 &
    REACT_PID=$!
    echo "   PID: $REACT_PID"
    cd ..

    echo ""
    echo -e "${GREEN}✅ Servers ξεκίνησαν!${NC}"
    echo ""
    echo -e "${BLUE}Logs:${NC}"
    echo "  • Django: tail -f django.log"
    echo "  • React: tail -f react.log"
    echo ""
    echo -e "${BLUE}Τερματισμός:${NC}"
    echo "  • kill $DJANGO_PID $REACT_PID"
    echo "  • ή: pkill -f 'manage.py runserver'"
    echo ""

    # Save PIDs to file
    echo "$DJANGO_PID" > .dev_pids
    echo "$REACT_PID" >> .dev_pids

    echo -e "${YELLOW}💡 Για να δεις τα logs σε πραγματικό χρόνο:${NC}"
    echo "   tail -f django.log react.log"
    echo ""
    echo -e "${YELLOW}💡 Για να σταματήσεις τους servers:${NC}"
    echo "   kill \$(cat .dev_pids)"
fi
