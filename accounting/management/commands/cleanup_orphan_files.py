# -*- coding: utf-8 -*-
"""
Management command to find and optionally clean up orphan files.

Orphan files are files that exist in the media/clients folder but
are not referenced by any ClientDocument in the database.

Usage:
    # Just list orphan files (dry run)
    python manage.py cleanup_orphan_files

    # List with file sizes
    python manage.py cleanup_orphan_files --verbose

    # Actually delete orphan files
    python manage.py cleanup_orphan_files --delete

    # Delete with confirmation prompt
    python manage.py cleanup_orphan_files --delete --confirm

    # Export list to file
    python manage.py cleanup_orphan_files --output orphans.txt

Author: LogistikoCRM
Version: 1.0
"""

import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from accounting.models import ClientDocument


class Command(BaseCommand):
    help = 'Find and optionally clean up orphan files in the media/clients folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete orphan files (default is dry run)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Ask for confirmation before deleting',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information including file sizes',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Write orphan file list to specified file',
        )
        parser.add_argument(
            '--older-than',
            type=int,
            help='Only process files older than N days',
        )

    def handle(self, *args, **options):
        delete_mode = options['delete']
        confirm = options['confirm']
        verbose = options['verbose']
        output_file = options.get('output')
        older_than_days = options.get('older_than')

        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('Αναζήτηση ορφανών αρχείων'))
        self.stdout.write(self.style.NOTICE('=' * 60))

        # Get all file paths from database
        db_files = set()
        for doc in ClientDocument.objects.all():
            if doc.file:
                # Get relative path from MEDIA_ROOT
                try:
                    db_files.add(doc.file.path)
                except (ValueError, AttributeError):
                    pass

        self.stdout.write(f'Αρχεία στη βάση: {len(db_files)}')

        # Scan clients folder
        clients_path = os.path.join(settings.MEDIA_ROOT, 'clients')
        if not os.path.exists(clients_path):
            self.stdout.write(self.style.WARNING(f'Ο φάκελος {clients_path} δεν υπάρχει'))
            return

        # Find all files in clients folder
        orphan_files = []
        total_size = 0
        now = datetime.now()

        for root, dirs, files in os.walk(clients_path):
            for filename in files:
                # Skip INFO.txt and other system files
                if filename in ['INFO.txt', '.DS_Store', 'Thumbs.db']:
                    continue

                file_path = os.path.join(root, filename)

                # Check age if specified
                if older_than_days:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    age_days = (now - file_mtime).days
                    if age_days < older_than_days:
                        continue

                # Check if file is in database
                if file_path not in db_files:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    orphan_files.append({
                        'path': file_path,
                        'size': file_size,
                        'mtime': datetime.fromtimestamp(os.path.getmtime(file_path)),
                    })

        # Report findings
        if not orphan_files:
            self.stdout.write(self.style.SUCCESS('Δεν βρέθηκαν ορφανά αρχεία!'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.WARNING(f'Βρέθηκαν {len(orphan_files)} ορφανά αρχεία'))
        self.stdout.write(f'Συνολικό μέγεθος: {self._format_size(total_size)}')
        self.stdout.write('')

        # Output file list
        output_lines = []

        if verbose:
            self.stdout.write('Λίστα ορφανών αρχείων:')
            self.stdout.write('-' * 60)

        for idx, orphan in enumerate(orphan_files, 1):
            rel_path = os.path.relpath(orphan['path'], settings.MEDIA_ROOT)
            line = f"{idx}. {rel_path}"

            if verbose:
                line += f" ({self._format_size(orphan['size'])})"
                line += f" - {orphan['mtime'].strftime('%d/%m/%Y')}"

            output_lines.append(orphan['path'])

            if verbose or len(orphan_files) <= 20:
                self.stdout.write(line)

        if not verbose and len(orphan_files) > 20:
            self.stdout.write(f'(Χρησιμοποιήστε --verbose για πλήρη λίστα)')

        # Write to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f'# Orphan files report - {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
                f.write(f'# Total: {len(orphan_files)} files, {self._format_size(total_size)}\n\n')
                for path in output_lines:
                    f.write(path + '\n')
            self.stdout.write(self.style.SUCCESS(f'Η λίστα αποθηκεύτηκε στο: {output_file}'))

        # Delete if requested
        if delete_mode:
            self.stdout.write('')

            if confirm:
                user_input = input(f'Θέλετε να διαγράψετε {len(orphan_files)} ορφανά αρχεία; (yes/no): ')
                if user_input.lower() not in ['yes', 'y', 'ναι']:
                    self.stdout.write(self.style.NOTICE('Ακυρώθηκε'))
                    return

            deleted_count = 0
            deleted_size = 0
            errors = []

            for orphan in orphan_files:
                try:
                    os.remove(orphan['path'])
                    deleted_count += 1
                    deleted_size += orphan['size']

                    if verbose:
                        self.stdout.write(f'Διαγράφηκε: {orphan["path"]}')

                except Exception as e:
                    errors.append((orphan['path'], str(e)))

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(
                f'Διαγράφηκαν {deleted_count} αρχεία ({self._format_size(deleted_size)})'
            ))

            if errors:
                self.stdout.write(self.style.ERROR(f'Αποτυχίες: {len(errors)}'))
                for path, error in errors:
                    self.stdout.write(self.style.ERROR(f'  - {path}: {error}'))

            # Clean up empty directories
            self._cleanup_empty_dirs(clients_path)

        else:
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(
                'Dry run - χρησιμοποιήστε --delete για πραγματική διαγραφή'
            ))

    def _format_size(self, size_bytes):
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'

    def _cleanup_empty_dirs(self, root_path):
        """Remove empty directories"""
        removed = 0
        for root, dirs, files in os.walk(root_path, topdown=False):
            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                try:
                    # Only remove if empty
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        removed += 1
                except Exception:
                    pass

        if removed > 0:
            self.stdout.write(f'Διαγράφηκαν {removed} άδειοι φάκελοι')
