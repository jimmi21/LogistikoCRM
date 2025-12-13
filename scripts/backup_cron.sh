#!/bin/bash
#
# Automated backup script for D.P. Economy
# Add to crontab for production deployment
#
# Example crontab entry (daily backup at 2 AM):
# 0 2 * * * /path/to/D.P. Economy/scripts/backup_cron.sh >> /var/log/logistikocrm_backup.log 2>&1
#

set -e  # Exit on error

# Configuration
PROJECT_DIR="/path/to/D.P. Economy"  # UPDATE THIS!
VENV_DIR="/path/to/venv"              # UPDATE THIS!
BACKUP_DIR="/var/backups/logistikocrm"
KEEP_DAYS=30

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Change to project directory
cd "${PROJECT_DIR}"

# Run backup
echo "========================================"
echo "Starting backup: $(date)"
echo "========================================"

python manage.py backup_database \
    --output-dir "${BACKUP_DIR}" \
    --keep-days "${KEEP_DAYS}"

echo "Backup completed: $(date)"
echo ""

# Optional: Send notification email on success
# echo "Backup completed successfully" | mail -s "D.P. Economy Backup Success" admin@example.com
