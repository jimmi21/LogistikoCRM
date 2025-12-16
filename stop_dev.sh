#!/bin/bash
# Τερματισμός Django + React Development Servers
# Χρήση: ./stop_dev.sh

echo "🛑 Τερματισμός LogistikoCRM Development Servers..."

# Χρώματα
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Αν υπάρχει .dev_pids file
if [ -f ".dev_pids" ]; then
    echo -e "${YELLOW}Τερματισμός processes από .dev_pids...${NC}"
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Killing PID: $pid"
            kill $pid
        fi
    done < .dev_pids
    rm .dev_pids
    echo -e "${GREEN}✅ Processes από .dev_pids τερματίστηκαν${NC}"
fi

# Βρες και τερμάτισε Django runserver
DJANGO_PIDS=$(ps aux | grep '[m]anage.py runserver' | awk '{print $2}')
if [ ! -z "$DJANGO_PIDS" ]; then
    echo -e "${YELLOW}Τερματισμός Django servers...${NC}"
    echo "$DJANGO_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✅ Django servers τερματίστηκαν${NC}"
fi

# Βρες και τερμάτισε React/Vite dev server
VITE_PIDS=$(ps aux | grep '[v]ite' | awk '{print $2}')
if [ ! -z "$VITE_PIDS" ]; then
    echo -e "${YELLOW}Τερματισμός React/Vite servers...${NC}"
    echo "$VITE_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✅ React/Vite servers τερματίστηκαν${NC}"
fi

# Αν υπάρχει tmux session
if command -v tmux &> /dev/null; then
    if tmux has-session -t logistikocrm 2>/dev/null; then
        echo -e "${YELLOW}Τερματισμός tmux session 'logistikocrm'...${NC}"
        tmux kill-session -t logistikocrm
        echo -e "${GREEN}✅ Tmux session τερματίστηκε${NC}"
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Όλοι οι development servers τερματίστηκαν!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
