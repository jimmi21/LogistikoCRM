# -*- coding: utf-8 -*-
"""
Management command for quick backup using Django dumpdata.
More portable than database-specific backups (pg_dump).

Usage:
    python manage.py quick_backup
    python manage.py quick_backup --notes "Before major update"
    python manage.py quick_backup --no-media
"""
from django.core.management.base import BaseCommand, CommandError

from settings.backup_utils import create_backup
from settings.models import BackupSettings


class Command(BaseCommand):
    help = 'Create a portable backup using Django dumpdata (ZIP format)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--notes',
            type=str,
            default='',
            help='Add notes to this backup'
        )
        parser.add_argument(
            '--no-media',
            action='store_true',
            help='Skip backing up media files (faster)'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Minimal output'
        )

    def handle(self, *args, **options):
        notes = options['notes']
        include_media = not options['no_media']
        quiet = options['quiet']

        if not quiet:
            settings_obj = BackupSettings.get_settings()
            self.stdout.write(f'📁 Backup directory: {settings_obj.get_backup_dir()}')
            self.stdout.write(f'📦 Include media: {include_media}')
            self.stdout.write('🔄 Creating backup...')

        try:
            backup = create_backup(
                user=None,
                include_media=include_media,
                notes=notes or 'CLI backup'
            )

            if quiet:
                self.stdout.write(backup.file_path)
            else:
                self.stdout.write(self.style.SUCCESS(f'\n✅ Backup created successfully!'))
                self.stdout.write(f'   📄 File: {backup.filename}')
                self.stdout.write(f'   📏 Size: {backup.file_size_display()}')
                self.stdout.write(f'   📍 Path: {backup.file_path}')

        except Exception as e:
            raise CommandError(f'❌ Backup failed: {e}')
