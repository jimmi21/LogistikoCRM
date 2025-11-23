from django.core.management.base import BaseCommand
import shutil
from datetime import datetime
from pathlib import Path
from django.conf import settings


class Command(BaseCommand):
    help = 'Backup της βάσης δεδομένων'

    def handle(self, *args, **options):
        # Backup directory
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Database path
        db_path = settings.DATABASES['default']['NAME']
        
        # Backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'crm_db_{timestamp}.backup'
        
        try:
            # Copy database
            shutil.copy2(db_path, backup_path)
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ Backup ολοκληρώθηκε: {backup_path.name}'
            ))
            
            # Cleanup old backups (keep last 30)
            backups = sorted(backup_dir.glob('*.backup'))
            if len(backups) > 30:
                for old_backup in backups[:-30]:
                    old_backup.unlink()
                    self.stdout.write(f'🗑️ Διαγράφηκε παλιό backup: {old_backup.name}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Σφάλμα: {str(e)}'))