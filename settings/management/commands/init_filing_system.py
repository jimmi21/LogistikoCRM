"""
Management command για αρχικοποίηση του συστήματος αρχειοθέτησης.

Δημιουργεί τη δομή φακέλων για όλους ή συγκεκριμένους πελάτες
βάσει των ρυθμίσεων στο FilingSystemSettings.

Usage:
    # Δημιουργία φακέλων για όλους τους πελάτες
    python manage.py init_filing_system

    # Μόνο για συγκεκριμένο πελάτη (με ΑΦΜ)
    python manage.py init_filing_system --afm 123456789

    # Δημιουργία για συγκεκριμένο έτος
    python manage.py init_filing_system --year 2025

    # Δημιουργία για εύρος ετών
    python manage.py init_filing_system --year-from 2020 --year-to 2025

    # Dry run - εμφάνιση χωρίς δημιουργία
    python manage.py init_filing_system --dry-run

    # Verbose output
    python manage.py init_filing_system --verbose
"""

import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as django_settings

from settings.models import FilingSystemSettings
from accounting.models import ClientProfile


class Command(BaseCommand):
    help = 'Αρχικοποίηση δομής φακέλων αρχειοθέτησης για πελάτες'

    def add_arguments(self, parser):
        parser.add_argument(
            '--afm',
            type=str,
            help='ΑΦΜ συγκεκριμένου πελάτη (αλλιώς όλοι οι ενεργοί)'
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Συγκεκριμένο έτος για δημιουργία φακέλων'
        )
        parser.add_argument(
            '--year-from',
            type=int,
            help='Αρχικό έτος (default: τρέχον - 1)'
        )
        parser.add_argument(
            '--year-to',
            type=int,
            help='Τελικό έτος (default: τρέχον)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Εμφάνιση φακέλων χωρίς δημιουργία'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Αναλυτική εμφάνιση'
        )
        parser.add_argument(
            '--only-permanent',
            action='store_true',
            help='Δημιουργία μόνο μόνιμων φακέλων (00_ΜΟΝΙΜΑ)'
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Συμπερίληψη και ανενεργών πελατών'
        )

    def handle(self, *args, **options):
        # Λήψη ρυθμίσεων
        filing_settings = FilingSystemSettings.get_settings()
        archive_root = filing_settings.get_archive_root()

        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(self.style.SUCCESS('ΑΡΧΙΚΟΠΟΙΗΣΗ ΣΥΣΤΗΜΑΤΟΣ ΑΡΧΕΙΟΘΕΤΗΣΗΣ'))
        self.stdout.write(f"{'=' * 60}\n")

        # Εμφάνιση ρυθμίσεων
        self.stdout.write(f"Archive Root: {archive_root}")
        self.stdout.write(f"Δομή: {filing_settings.get_folder_structure_display()}")
        self.stdout.write(f"Μόνιμος Φάκελος: {'Ναι' if filing_settings.enable_permanent_folder else 'Όχι'}")
        self.stdout.write(f"Ετήσιος Φάκελος: {'Ναι' if filing_settings.enable_yearend_folder else 'Όχι'}")
        self.stdout.write(f"Ελληνικοί Μήνες: {'Ναι' if filing_settings.use_greek_month_names else 'Όχι'}")
        self.stdout.write("")

        # Έλεγχος network path
        if filing_settings.use_network_storage and filing_settings.archive_root:
            if not os.path.exists(archive_root):
                self.stdout.write(self.style.WARNING(
                    f"⚠️  Ο κοινόχρηστος φάκελος δεν υπάρχει: {archive_root}"
                ))
                if not options['dry_run']:
                    try:
                        os.makedirs(archive_root, exist_ok=True)
                        self.stdout.write(self.style.SUCCESS(f"✓ Δημιουργήθηκε: {archive_root}"))
                    except PermissionError:
                        raise CommandError(f"Δεν υπάρχουν δικαιώματα για: {archive_root}")

        # Καθορισμός ετών
        current_year = datetime.now().year
        if options['year']:
            years = [options['year']]
        else:
            year_from = options['year_from'] or (current_year - 1)
            year_to = options['year_to'] or current_year
            years = list(range(year_from, year_to + 1))

        self.stdout.write(f"Έτη: {', '.join(map(str, years))}\n")

        # Λήψη πελατών
        clients = ClientProfile.objects.all()
        if options['afm']:
            clients = clients.filter(afm=options['afm'])
            if not clients.exists():
                raise CommandError(f"Δεν βρέθηκε πελάτης με ΑΦΜ: {options['afm']}")
        elif not options['include_inactive']:
            clients = clients.filter(is_active=True)

        client_count = clients.count()
        self.stdout.write(f"Πελάτες: {client_count}")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING("\n[DRY RUN - Καμία αλλαγή δεν θα γίνει]\n"))

        # Counters
        folders_created = 0
        folders_existing = 0
        errors = 0

        # Δημιουργία φακέλων
        for idx, client in enumerate(clients, 1):
            self.stdout.write(f"\n[{idx}/{client_count}] {client.eponimia} ({client.afm})")

            try:
                created, existing = self._create_client_folders(
                    client,
                    filing_settings,
                    archive_root,
                    years,
                    options
                )
                folders_created += created
                folders_existing += existing
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  ✗ Σφάλμα: {e}"))

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(self.style.SUCCESS('ΟΛΟΚΛΗΡΩΣΗ'))
        self.stdout.write(f"{'=' * 60}")
        self.stdout.write(f"Νέοι φάκελοι: {folders_created}")
        self.stdout.write(f"Υπάρχοντες: {folders_existing}")
        if errors:
            self.stdout.write(self.style.ERROR(f"Σφάλματα: {errors}"))

    def _create_client_folders(self, client, settings, archive_root, years, options):
        """Δημιουργεί τη δομή φακέλων για έναν πελάτη."""
        import re

        created = 0
        existing = 0
        dry_run = options['dry_run']
        verbose = options['verbose']
        only_permanent = options['only_permanent']

        # Καθαρισμός επωνυμίας
        safe_name = re.sub(r'[^\w\s-]', '', client.eponimia)[:30]
        safe_name = safe_name.replace(' ', '_').strip('_')

        # Base client folder
        client_folder = os.path.join(archive_root, 'clients', f"{client.afm}_{safe_name}")

        # === 1. ΜΟΝΙΜΟΣ ΦΑΚΕΛΟΣ (00_ΜΟΝΙΜΑ) ===
        if settings.enable_permanent_folder:
            permanent_path = os.path.join(client_folder, settings.permanent_folder_name)

            for category in settings.get_permanent_folder_categories():
                cat_path = os.path.join(permanent_path, category)
                c, e = self._ensure_folder(cat_path, dry_run, verbose)
                created += c
                existing += e

        if only_permanent:
            return created, existing

        # === 2. ΕΤΗΣΙΟΙ ΦΑΚΕΛΟΙ ===
        for year in years:
            year_path = os.path.join(client_folder, str(year))

            # Μηνιαίοι φάκελοι (01-12)
            for month in range(1, 13):
                month_name = settings.get_month_folder_name(month)
                month_path = os.path.join(year_path, month_name)

                for category in settings.get_monthly_folder_categories():
                    cat_path = os.path.join(month_path, category)
                    c, e = self._ensure_folder(cat_path, dry_run, verbose)
                    created += c
                    existing += e

            # === 3. ΕΤΗΣΙΟΣ ΦΑΚΕΛΟΣ (13_ΕΤΗΣΙΑ) ===
            if settings.enable_yearend_folder:
                yearend_path = os.path.join(year_path, settings.yearend_folder_name)

                for category in settings.get_yearend_folder_categories():
                    cat_path = os.path.join(yearend_path, category)
                    c, e = self._ensure_folder(cat_path, dry_run, verbose)
                    created += c
                    existing += e

        # === 4. INFO.txt ===
        info_path = os.path.join(client_folder, 'INFO.txt')
        if not os.path.exists(info_path) and not dry_run:
            try:
                os.makedirs(client_folder, exist_ok=True)
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(f"ΠΕΛΑΤΗΣ: {client.eponimia}\n")
                    f.write(f"ΑΦΜ: {client.afm}\n")
                    f.write(f"ΔΟΥ: {client.doy or '-'}\n")
                    f.write(f"Email: {client.email or '-'}\n")
                    f.write(f"Τηλέφωνο: {client.phone or '-'}\n")
                    f.write(f"Δημιουργία: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                    f.write(f"\n--- Δομή Φακέλων ---\n")
                    f.write(f"00_ΜΟΝΙΜΑ/ - Μόνιμα έγγραφα (συμβάσεις, καταστατικό)\n")
                    f.write(f"YYYY/MM/  - Μηνιαία έγγραφα ανά έτος\n")
                    f.write(f"YYYY/13_ΕΤΗΣΙΑ/ - Ετήσιες δηλώσεις (Ε1, Ε2, Ε3, ΕΝΦΙΑ)\n")
                if verbose:
                    self.stdout.write(f"    ✓ INFO.txt")
                created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ✗ INFO.txt: {e}"))

        return created, existing

    def _ensure_folder(self, path, dry_run, verbose):
        """Δημιουργεί φάκελο αν δεν υπάρχει."""
        if os.path.exists(path):
            if verbose:
                self.stdout.write(f"    - {path} (υπάρχει)")
            return 0, 1

        if dry_run:
            if verbose:
                self.stdout.write(f"    + {path} (θα δημιουργηθεί)")
            return 1, 0

        try:
            os.makedirs(path, exist_ok=True)
            if verbose:
                self.stdout.write(self.style.SUCCESS(f"    ✓ {path}"))
            return 1, 0
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    ✗ {path}: {e}"))
            return 0, 0
