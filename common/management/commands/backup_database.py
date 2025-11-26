"""
Management command to backup database and media files
Critical for production accounting office deployment

Usage:
    python manage.py backup_database [--output-dir /path/to/backups]
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Backup database and media files for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='/var/backups/logistikocrm',
            help='Directory to store backups (default: /var/backups/logistikocrm)'
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Number of days to keep old backups (default: 30)'
        )
        parser.add_argument(
            '--skip-media',
            action='store_true',
            help='Skip backing up media files'
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        keep_days = options['keep_days']
        skip_media = options['skip_media']

        # Create backup directory
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise CommandError(f'Failed to create backup directory: {e}')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}'

        self.stdout.write(self.style.SUCCESS(f'🔄 Starting backup: {backup_name}'))

        # Backup database
        try:
            db_backup_path = self._backup_database(output_dir, backup_name)
            self.stdout.write(self.style.SUCCESS(f'✅ Database backed up: {db_backup_path}'))
        except Exception as e:
            raise CommandError(f'❌ Database backup failed: {e}')

        # Backup media files
        if not skip_media:
            try:
                media_backup_path = self._backup_media(output_dir, backup_name)
                self.stdout.write(self.style.SUCCESS(f'✅ Media files backed up: {media_backup_path}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️ Media backup failed: {e}'))

        # Cleanup old backups
        self._cleanup_old_backups(output_dir, keep_days)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Backup completed: {backup_name}'))
        self.stdout.write(f'📁 Location: {output_dir}')

    def _backup_database(self, output_dir, backup_name):
        """Backup PostgreSQL or SQLite database"""
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']

        if 'postgresql' in engine:
            return self._backup_postgresql(output_dir, backup_name, db_config)
        elif 'sqlite' in engine:
            return self._backup_sqlite(output_dir, backup_name, db_config)
        else:
            raise CommandError(f'Unsupported database engine: {engine}')

    def _backup_postgresql(self, output_dir, backup_name, db_config):
        """Backup PostgreSQL database using pg_dump"""
        backup_file = output_dir / f'{backup_name}.sql.gz'

        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config.get('USER', 'postgres'),
            '-d', db_config.get('NAME'),
            '-F', 'c',  # Custom format (compressed)
            '-f', str(backup_file)
        ]

        # Set password via environment
        env = os.environ.copy()
        if db_config.get('PASSWORD'):
            env['PGPASSWORD'] = db_config['PASSWORD']

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f'pg_dump failed: {result.stderr}')

        return backup_file

    def _backup_sqlite(self, output_dir, backup_name, db_config):
        """Backup SQLite database"""
        import shutil

        db_path = Path(db_config['NAME'])
        backup_file = output_dir / f'{backup_name}.sqlite3'

        if not db_path.exists():
            raise Exception(f'Database file not found: {db_path}')

        # Close connections and copy
        connection.close()
        shutil.copy2(db_path, backup_file)

        return backup_file

    def _backup_media(self, output_dir, backup_name):
        """Backup media files using tar"""
        media_root = Path(settings.MEDIA_ROOT)

        if not media_root.exists():
            raise Exception(f'Media directory not found: {media_root}')

        backup_file = output_dir / f'{backup_name}_media.tar.gz'

        # Create compressed tar archive
        cmd = [
            'tar',
            '-czf',
            str(backup_file),
            '-C', str(media_root.parent),
            media_root.name
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f'tar failed: {result.stderr}')

        return backup_file

    def _cleanup_old_backups(self, output_dir, keep_days):
        """Remove backups older than keep_days"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0

        for backup_file in output_dir.glob('backup_*'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                removed_count += 1

        if removed_count > 0:
            self.stdout.write(f'🗑️ Removed {removed_count} old backups')
