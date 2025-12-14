# -*- coding: utf-8 -*-
"""
Management command to list available backups.

Usage:
    python manage.py list_backups
    python manage.py list_backups --all    # Include deleted/missing files
"""
from django.core.management.base import BaseCommand

from settings.models import BackupHistory, BackupSettings


class Command(BaseCommand):
    help = 'List available backups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all backups including missing files'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Number of backups to show (default: 20)'
        )

    def handle(self, *args, **options):
        show_all = options['all']
        limit = options['limit']

        settings_obj = BackupSettings.get_settings()

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('📋 BACKUP LIST'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'Backup directory: {settings_obj.get_backup_dir()}')
        self.stdout.write(f'Max backups: {settings_obj.max_backups or "unlimited"}')
        self.stdout.write('-' * 80)

        backups = BackupHistory.objects.order_by('-created_at')[:limit]

        if not backups:
            self.stdout.write(self.style.WARNING('\nNo backups found.'))
            self.stdout.write('Create one with: python manage.py quick_backup\n')
            return

        self.stdout.write(
            f'\n{"ID":<5} {"Created":<18} {"Size":<10} {"DB":<4} {"Media":<6} '
            f'{"File":<6} {"Filename"}'
        )
        self.stdout.write('-' * 80)

        for b in backups:
            exists = self.style.SUCCESS('✓') if b.file_exists() else self.style.ERROR('✗')

            if not show_all and not b.file_exists():
                continue

            db = '✓' if b.includes_db else '-'
            media = '✓' if b.includes_media else '-'
            date_str = b.created_at.strftime('%d/%m/%Y %H:%M')

            restored = ''
            if b.restored_at:
                restored = f' [restored {b.restored_at.strftime("%d/%m")}]'

            self.stdout.write(
                f'{b.id:<5} {date_str:<18} {b.file_size_display():<10} {db:<4} {media:<6} '
                f'{exists}     {b.filename}{restored}'
            )

        self.stdout.write('-' * 80)

        # Summary
        total = BackupHistory.objects.count()
        existing = sum(1 for b in BackupHistory.objects.all() if b.file_exists())
        self.stdout.write(f'\nTotal: {total} backups ({existing} files exist)')

        self.stdout.write('\nQuick commands:')
        self.stdout.write('  python manage.py quick_backup           # Create backup')
        self.stdout.write('  python manage.py quick_restore --latest # Restore latest')
        self.stdout.write('  python manage.py quick_restore --id <N> # Restore specific')
        self.stdout.write('')
