"""
Management command to restore database and media files from backup
Critical for disaster recovery in production accounting office

Usage:
    python manage.py restore_database <backup_name> [--backup-dir /path/to/backups] [--skip-media]

WARNING: This will OVERWRITE your current database! Make sure you have a backup first.
"""
import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Restore database and media files from backup'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_name',
            type=str,
            help='Name of the backup to restore (e.g., backup_20241126_143022)'
        )
        parser.add_argument(
            '--backup-dir',
            type=str,
            default='/var/backups/logistikocrm',
            help='Directory containing backups (default: /var/backups/logistikocrm)'
        )
        parser.add_argument(
            '--skip-media',
            action='store_true',
            help='Skip restoring media files'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt (DANGEROUS!)'
        )

    def handle(self, *args, **options):
        backup_name = options['backup_name']
        backup_dir = Path(options['backup_dir'])
        skip_media = options['skip_media']
        auto_confirm = options['yes']

        if not backup_dir.exists():
            raise CommandError(f'Backup directory not found: {backup_dir}')

        # Safety confirmation
        if not auto_confirm:
            self.stdout.write(self.style.WARNING(
                '\n⚠️ WARNING: This will OVERWRITE your current database!\n'
                'Make sure you have a recent backup before proceeding.\n'
            ))
            confirm = input('Type "YES" to continue: ')
            if confirm != 'YES':
                self.stdout.write('Restore cancelled.')
                return

        self.stdout.write(self.style.SUCCESS(f'🔄 Starting restore: {backup_name}'))

        # Restore database
        try:
            self._restore_database(backup_dir, backup_name)
            self.stdout.write(self.style.SUCCESS('✅ Database restored successfully'))
        except Exception as e:
            raise CommandError(f'❌ Database restore failed: {e}')

        # Restore media files
        if not skip_media:
            try:
                self._restore_media(backup_dir, backup_name)
                self.stdout.write(self.style.SUCCESS('✅ Media files restored successfully'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️ Media restore failed: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Restore completed: {backup_name}'))

    def _restore_database(self, backup_dir, backup_name):
        """Restore PostgreSQL or SQLite database"""
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']

        if 'postgresql' in engine:
            return self._restore_postgresql(backup_dir, backup_name, db_config)
        elif 'sqlite' in engine:
            return self._restore_sqlite(backup_dir, backup_name, db_config)
        else:
            raise CommandError(f'Unsupported database engine: {engine}')

    def _restore_postgresql(self, backup_dir, backup_name, db_config):
        """Restore PostgreSQL database using pg_restore"""
        backup_file = backup_dir / f'{backup_name}.sql.gz'

        if not backup_file.exists():
            raise Exception(f'Backup file not found: {backup_file}')

        # Drop and recreate database
        db_name = db_config.get('NAME')
        self.stdout.write(f'🔄 Dropping and recreating database: {db_name}')

        # Build pg_restore command
        cmd = [
            'pg_restore',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config.get('USER', 'postgres'),
            '-d', db_name,
            '-c',  # Clean (drop) database objects before recreating
            '-F', 'c',  # Custom format
            str(backup_file)
        ]

        # Set password via environment
        env = os.environ.copy()
        if db_config.get('PASSWORD'):
            env['PGPASSWORD'] = db_config['PASSWORD']

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f'pg_restore failed: {result.stderr}')

    def _restore_sqlite(self, backup_dir, backup_name, db_config):
        """Restore SQLite database"""
        import shutil

        backup_file = backup_dir / f'{backup_name}.sqlite3'

        if not backup_file.exists():
            raise Exception(f'Backup file not found: {backup_file}')

        db_path = Path(db_config['NAME'])

        # Close connections and replace
        connection.close()

        # Backup current database before replacing
        if db_path.exists():
            current_backup = db_path.with_suffix('.sqlite3.before_restore')
            shutil.copy2(db_path, current_backup)
            self.stdout.write(f'📋 Current database backed up to: {current_backup}')

        # Restore from backup
        shutil.copy2(backup_file, db_path)

    def _restore_media(self, backup_dir, backup_name):
        """Restore media files from tar archive"""
        backup_file = backup_dir / f'{backup_name}_media.tar.gz'

        if not backup_file.exists():
            raise Exception(f'Media backup file not found: {backup_file}')

        media_root = Path(settings.MEDIA_ROOT)

        # Backup current media before replacing
        if media_root.exists():
            import shutil
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            media_backup = media_root.parent / f'media_before_restore_{timestamp}'
            shutil.copytree(media_root, media_backup)
            self.stdout.write(f'📋 Current media backed up to: {media_backup}')

        # Extract tar archive
        cmd = [
            'tar',
            '-xzf',
            str(backup_file),
            '-C', str(media_root.parent)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f'tar extraction failed: {result.stderr}')
