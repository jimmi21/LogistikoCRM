#!/bin/bash
# LogistikoCRM - Εύκολη Εκκίνηση
# Χρήση: ./start.sh [option]
#
# Επιλογές:
#   dev      - Development με SQLite (γρήγορο)
#   prod     - Production με PostgreSQL + Redis + Celery
#   stop     - Σταμάτημα όλων των containers
#   logs     - Προβολή logs
#   shell    - Django shell
#   migrate  - Εφαρμογή migrations
#   backup   - Backup database

set -e

# Χρώματα για output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Βρίσκει την IP του μηχανήματος
get_local_ip() {
    hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost"
}

LOCAL_IP=$(get_local_ip)

show_help() {
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         LogistikoCRM - Εκκίνηση              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Χρήση: ./start.sh [επιλογή]"
    echo ""
    echo "Επιλογές:"
    echo "  dev      Εκκίνηση development server (SQLite)"
    echo "  prod     Εκκίνηση production (PostgreSQL + Redis)"
    echo "  stop     Σταμάτημα containers"
    echo "  restart  Επανεκκίνηση"
    echo "  logs     Προβολή logs"
    echo "  shell    Django shell"
    echo "  migrate  Εφαρμογή migrations"
    echo "  backup   Backup database"
    echo "  status   Κατάσταση services"
    echo ""
}

case "${1:-help}" in
    dev)
        echo -e "${GREEN}Εκκίνηση Development Server...${NC}"

        # Έλεγχος αν υπάρχει Docker
        if command -v docker &> /dev/null && command -v docker compose &> /dev/null; then
            echo "Χρήση Docker..."
            docker compose -f docker-compose.dev.yml up --build
        else
            echo "Χρήση Python απευθείας..."
            # Ενεργοποίηση venv αν υπάρχει
            if [ -f "venv/bin/activate" ]; then
                source venv/bin/activate
            fi

            python manage.py migrate --noinput
            echo -e "${GREEN}════════════════════════════════════════${NC}"
            echo -e "${GREEN}Server ξεκίνησε!${NC}"
            echo -e "Τοπική πρόσβαση:  http://localhost:8000"
            echo -e "LAN πρόσβαση:     http://${LOCAL_IP}:8000"
            echo -e "${GREEN}════════════════════════════════════════${NC}"
            python manage.py runserver 0.0.0.0:8000
        fi
        ;;

    prod)
        echo -e "${GREEN}Εκκίνηση Production Environment...${NC}"
        docker compose up -d --build
        echo ""
        echo -e "${GREEN}════════════════════════════════════════${NC}"
        echo -e "${GREEN}LogistikoCRM ξεκίνησε!${NC}"
        echo -e "Πρόσβαση:  http://${LOCAL_IP}:8000"
        echo -e "Admin:     http://${LOCAL_IP}:8000/admin"
        echo -e "${GREEN}════════════════════════════════════════${NC}"
        docker compose logs -f web
        ;;

    stop)
        echo -e "${YELLOW}Σταμάτημα containers...${NC}"
        docker compose down 2>/dev/null || true
        docker compose -f docker-compose.dev.yml down 2>/dev/null || true
        echo -e "${GREEN}Ολοκληρώθηκε!${NC}"
        ;;

    restart)
        echo -e "${YELLOW}Επανεκκίνηση...${NC}"
        docker compose restart
        ;;

    logs)
        docker compose logs -f ${2:-web}
        ;;

    shell)
        if docker ps | grep -q logistiko_web; then
            docker exec -it logistiko_web python manage.py shell
        elif docker ps | grep -q logistiko_dev; then
            docker exec -it logistiko_dev python manage.py shell
        else
            python manage.py shell
        fi
        ;;

    migrate)
        if docker ps | grep -q logistiko_web; then
            docker exec -it logistiko_web python manage.py migrate
        elif docker ps | grep -q logistiko_dev; then
            docker exec -it logistiko_dev python manage.py migrate
        else
            python manage.py migrate
        fi
        ;;

    backup)
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        echo -e "${GREEN}Δημιουργία backup: ${BACKUP_FILE}${NC}"
        if docker ps | grep -q logistiko_db; then
            docker exec logistiko_db pg_dump -U logistiko logistikocrm > "backups/${BACKUP_FILE}"
        else
            cp db.sqlite3 "backups/db_$(date +%Y%m%d_%H%M%S).sqlite3"
        fi
        echo -e "${GREEN}Backup ολοκληρώθηκε!${NC}"
        ;;

    status)
        echo -e "${GREEN}Κατάσταση Services:${NC}"
        docker compose ps
        ;;

    *)
        show_help
        ;;
esac
