# -*- coding: utf-8 -*-
"""
Management command for restoring backups created by quick_backup.

Usage:
    python manage.py quick_restore              # Interactive - shows list
    python manage.py quick_restore --latest     # Restore latest backup
    python manage.py quick_restore --id 5       # Restore backup with ID 5
    python manage.py quick_restore --file backup_20241201.zip  # By filename

WARNING: 'replace' mode will OVERWRITE your current database!
"""
from django.core.management.base import BaseCommand, CommandError

from settings.backup_utils import restore_backup, validate_backup_file
from settings.models import BackupHistory


class Command(BaseCommand):
    help = 'Restore from a backup created by quick_backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Backup ID to restore'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Backup filename to restore'
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Restore the most recent backup'
        )
        parser.add_argument(
            '--mode',
            type=str,
            choices=['replace', 'merge'],
            default='replace',
            help='Restore mode: replace (default) or merge'
        )
        parser.add_argument(
            '--no-safety-backup',
            action='store_true',
            help='Skip creating safety backup before restore (not recommended!)'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt (DANGEROUS!)'
        )

    def handle(self, *args, **options):
        backup_id = options.get('id')
        filename = options.get('file')
        use_latest = options.get('latest')
        mode = options['mode']
        skip_safety = options['no_safety_backup']
        auto_confirm = options['yes']

        # Determine which backup to restore
        backup = None

        if backup_id:
            try:
                backup = BackupHistory.objects.get(pk=backup_id)
            except BackupHistory.DoesNotExist:
                raise CommandError(f'Backup with ID {backup_id} not found')

        elif filename:
            try:
                backup = BackupHistory.objects.get(filename__icontains=filename)
            except BackupHistory.DoesNotExist:
                raise CommandError(f'Backup with filename "{filename}" not found')
            except BackupHistory.MultipleObjectsReturned:
                raise CommandError(f'Multiple backups match "{filename}". Use --id instead.')

        elif use_latest:
            backup = BackupHistory.objects.order_by('-created_at').first()
            if not backup:
                raise CommandError('No backups found')

        else:
            # Interactive mode - show list
            self._show_backup_list()
            return

        # Validate backup exists
        if not backup.file_exists():
            raise CommandError(f'Backup file not found: {backup.file_path}')

        # Validate backup file
        is_valid, error_msg = validate_backup_file(backup.file_path)
        if not is_valid:
            raise CommandError(f'Invalid backup file: {error_msg}')

        # Show info and confirm
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.WARNING('📦 BACKUP RESTORE'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'   Backup:  {backup.filename}')
        self.stdout.write(f'   Created: {backup.created_at.strftime("%d/%m/%Y %H:%M")}')
        self.stdout.write(f'   Size:    {backup.file_size_display()}')
        self.stdout.write(f'   Mode:    {mode}')
        self.stdout.write(f'   Safety:  {"No" if skip_safety else "Yes"}')
        if backup.notes:
            self.stdout.write(f'   Notes:   {backup.notes}')
        self.stdout.write('=' * 50 + '\n')

        if mode == 'replace':
            self.stdout.write(self.style.ERROR(
                '⚠️  WARNING: This will OVERWRITE your current database!\n'
            ))

        # Confirmation
        if not auto_confirm:
            confirm = input('Type "YES" to continue: ')
            if confirm != 'YES':
                self.stdout.write('Restore cancelled.')
                return

        # Perform restore
        self.stdout.write('🔄 Restoring backup...')

        result = restore_backup(
            backup.id,
            user=None,
            mode=mode,
            create_safety_backup=not skip_safety
        )

        if result['success']:
            self.stdout.write(self.style.SUCCESS('\n✅ Restore completed successfully!'))
            if result.get('safety_backup_id'):
                safety = BackupHistory.objects.get(pk=result['safety_backup_id'])
                self.stdout.write(f'   Safety backup: {safety.filename}')
        else:
            raise CommandError(f'❌ Restore failed: {result.get("error", "Unknown error")}')

    def _show_backup_list(self):
        """Show interactive list of available backups."""
        backups = BackupHistory.objects.order_by('-created_at')[:20]

        if not backups:
            self.stdout.write(self.style.WARNING('No backups found.'))
            self.stdout.write('Run: python manage.py quick_backup')
            return

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📋 AVAILABLE BACKUPS'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'{"ID":<5} {"Date":<18} {"Size":<10} {"Media":<6} {"Filename"}')
        self.stdout.write('-' * 70)

        for b in backups:
            exists = '✓' if b.file_exists() else '✗'
            media = '✓' if b.includes_media else '-'
            date_str = b.created_at.strftime('%d/%m/%Y %H:%M')
            self.stdout.write(
                f'{b.id:<5} {date_str:<18} {b.file_size_display():<10} {media:<6} {exists} {b.filename}'
            )

        self.stdout.write('-' * 70)
        self.stdout.write('\nUsage:')
        self.stdout.write('  python manage.py quick_restore --id <ID>')
        self.stdout.write('  python manage.py quick_restore --latest')
        self.stdout.write('  python manage.py quick_restore --latest --mode merge')
        self.stdout.write('')
