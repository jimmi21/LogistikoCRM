"""
Generate Monthly Obligations - Professional Management Command
Author: ddiplas
Version: 3.0 TURBO
Features: Progress bar, dry-run, email notifications, detailed logging
"""

import sys
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from accounting.models import ClientObligation, MonthlyObligation, ClientProfile
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Setup logger
logger = logging.getLogger('accounting.obligations')


class Command(BaseCommand):
    help = '🚀 Δημιουργία μηνιαίων υποχρεώσεων με advanced features'
    
    def __init__(self):
        super().__init__()
        self.created_obligations = []
        self.skipped_obligations = []
        self.errors = []
        self.stats = defaultdict(int)
    
    def add_arguments(self, parser):
        """Enhanced arguments με περισσότερες επιλογές"""
        parser.add_argument(
            '--year',
            type=int,
            help='Έτος (default: τρέχον έτος)'
        )
        parser.add_argument(
            '--month',
            type=int,
            help='Μήνας (default: επόμενος μήνας)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='🧪 Δοκιμαστική εκτέλεση (δεν αποθηκεύει)'
        )
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='📧 Αποστολή email report'
        )
        parser.add_argument(
            '--client',
            type=str,
            help='ΑΦΜ συγκεκριμένου πελάτη (για testing)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='⚡ Αναδημιουργία υπαρχουσών υποχρεώσεων'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='🤫 Minimal output'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='📢 Detailed output'
        )
    
    def handle(self, *args, **kwargs):
        """Main handler με error handling"""
        try:
            # Parse arguments
            self.parse_arguments(kwargs)
            
            # Header
            if not self.quiet:
                self.print_header()
            
            # Main process
            with transaction.atomic():
                if self.dry_run:
                    self.stdout.write(self.style.WARNING('\n🧪 DRY-RUN MODE - Δεν θα γίνουν αλλαγές!\n'))
                
                self.process_obligations()
                
                if self.dry_run:
                    transaction.set_rollback(True)
            
            # Results
            self.print_results()
            
            # Send email if requested
            if self.send_email:
                self.send_report_email()
            
            # Log to file
            self.log_results()
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR('\n\n❌ Διακόπηκε από τον χρήστη!'))
            sys.exit(1)
        except Exception as e:
            logger.error(f"Critical error: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR(f'\n💥 Κρίσιμο σφάλμα: {str(e)}'))
            raise CommandError(str(e))
    
    def parse_arguments(self, kwargs):
        """Parse and validate arguments"""
        now = timezone.now()
        
        # Default to next month
        self.year = kwargs.get('year') or now.year
        self.month = kwargs.get('month')
        
        if not self.month:
            # Default to next month
            if now.month == 12:
                self.month = 1
                self.year = now.year + 1
            else:
                self.month = now.month + 1
        
        # Validate month
        if not 1 <= self.month <= 12:
            raise CommandError(f'❌ Μη έγκυρος μήνας: {self.month}')
        
        # Other options
        self.dry_run = kwargs.get('dry_run', False)
        self.send_email = kwargs.get('send_email', False)
        self.client_afm = kwargs.get('client')
        self.force = kwargs.get('force', False)
        self.quiet = kwargs.get('quiet', False)
        self.verbose = kwargs.get('verbose', False)
    
    def print_header(self):
        """Print beautiful header"""
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS(
            '    🚀 ΔΗΜΙΟΥΡΓΙΑ ΜΗΝΙΑΙΩΝ ΥΠΟΧΡΕΩΣΕΩΝ    '
        ))
        self.stdout.write('=' * 70)
        
        month_names = ['', 'Ιανουάριος', 'Φεβρουάριος', 'Μάρτιος', 'Απρίλιος', 
                      'Μάιος', 'Ιούνιος', 'Ιούλιος', 'Αύγουστος', 'Σεπτέμβριος', 
                      'Οκτώβριος', 'Νοέμβριος', 'Δεκέμβριος']
        
        self.stdout.write(f'\n📅 Περίοδος: {self.style.WARNING(f"{month_names[self.month]} {self.year}")}')
        self.stdout.write(f'🕐 Εκτέλεση: {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}')
        
        if self.client_afm:
            self.stdout.write(f'👤 Μόνο για: {self.client_afm}')
        
        self.stdout.write('-' * 70)
    
    def process_obligations(self):
        """Process obligations με progress tracking"""
        # Get client obligations
        query = ClientObligation.objects.filter(is_active=True)
        
        if self.client_afm:
            query = query.filter(client__afm=self.client_afm)
        
        client_obligations = query.select_related('client').prefetch_related(
            'obligation_types', 'obligation_profiles__obligations'
        )
        
        total_clients = client_obligations.count()
        
        if total_clients == 0:
            self.stdout.write(self.style.WARNING('⚠️  Δεν βρέθηκαν ενεργοί πελάτες!'))
            return
        
        if not self.quiet:
            self.stdout.write(f'\n🔍 Βρέθηκαν {self.style.SUCCESS(str(total_clients))} πελάτες με υποχρεώσεις\n')
        
        # Progress tracking
        for idx, client_obl in enumerate(client_obligations, 1):
            if not self.quiet:
                self.show_progress(idx, total_clients, f'Επεξεργασία: {client_obl.client.eponimia[:30]}')
            
            self.process_client(client_obl)
        
        if not self.quiet:
            self.stdout.write('\n')  # New line after progress
    
    def process_client(self, client_obl):
        """Process single client obligations"""
        client = client_obl.client
        obligation_types = client_obl.get_all_obligation_types()
        
        for obligation_type in obligation_types:
            try:
                # Check if applies to month
                if not obligation_type.applies_to_month(self.month):
                    if self.verbose:
                        self.stdout.write(
                            f'  ⏭️  Skip: {obligation_type.name} - δεν ισχύει για μήνα {self.month}'
                        )
                    continue
                
                # Calculate deadline
                deadline = obligation_type.get_deadline_for_month(self.year, self.month)
                
                if not deadline:
                    self.errors.append(f'{client.eponimia} - {obligation_type.name}: No deadline')
                    continue
                
                # Create or update
                if self.force:
                    # Force recreate
                    MonthlyObligation.objects.filter(
                        client=client,
                        obligation_type=obligation_type,
                        year=self.year,
                        month=self.month
                    ).delete()
                    created = True
                    monthly_obl = MonthlyObligation.objects.create(
                        client=client,
                        obligation_type=obligation_type,
                        year=self.year,
                        month=self.month,
                        deadline=deadline,
                        status='pending'
                    )
                else:
                    # Get or create
                    monthly_obl, created = MonthlyObligation.objects.get_or_create(
                        client=client,
                        obligation_type=obligation_type,
                        year=self.year,
                        month=self.month,
                        defaults={
                            'deadline': deadline,
                            'status': 'pending',
                            'hourly_rate': 50.00  # Default rate
                        }
                    )
                
                if created:
                    self.created_obligations.append(monthly_obl)
                    self.stats['created'] += 1
                    self.stats[obligation_type.name] += 1
                    
                    if self.verbose and not self.quiet:
                        self.stdout.write(
                            f'  ✅ {client.eponimia[:30]} - {obligation_type.name} '
                            f'(Προθεσμία: {deadline.strftime("%d/%m/%Y")})'
                        )
                else:
                    self.skipped_obligations.append(monthly_obl)
                    self.stats['skipped'] += 1
                    
            except Exception as e:
                self.errors.append(f'{client.eponimia} - {obligation_type.name}: {str(e)}')
                logger.error(f"Error processing {client.afm}: {str(e)}")
    
    def show_progress(self, current, total, message=''):
        """Show progress bar"""
        bar_length = 40
        percent = float(current) / total
        arrow = '█' * int(round(percent * bar_length))
        spaces = '░' * (bar_length - len(arrow))
        
        sys.stdout.write(f'\r[{arrow}{spaces}] {int(percent*100)}% - {message[:40]:<40}')
        sys.stdout.flush()
    
    def print_results(self):
        """Print detailed results"""
        if self.quiet:
            self.stdout.write(f'Created: {self.stats["created"]}, Skipped: {self.stats["skipped"]}')
            return
        
        self.stdout.write('\n')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('    📊 ΑΠΟΤΕΛΕΣΜΑΤΑ    '))
        self.stdout.write('=' * 70)
        
        # Summary
        self.stdout.write(f'\n✅ Δημιουργήθηκαν: {self.style.SUCCESS(str(self.stats["created"]))} υποχρεώσεις')
        self.stdout.write(f'⏭️  Υπήρχαν ήδη: {self.style.WARNING(str(self.stats["skipped"]))}')
        
        if self.errors:
            self.stdout.write(f'❌ Σφάλματα: {self.style.ERROR(str(len(self.errors)))}')
            if self.verbose:
                for error in self.errors[:5]:  # Show first 5 errors
                    self.stdout.write(f'   • {error}')
        
        # Statistics by type
        if self.verbose and self.stats['created'] > 0:
            self.stdout.write('\n📈 Ανά τύπο υποχρέωσης:')
            for key, value in sorted(self.stats.items()):
                if key not in ['created', 'skipped'] and value > 0:
                    self.stdout.write(f'   • {key}: {value}')
        
        # Database statistics
        total_pending = MonthlyObligation.objects.filter(
            year=self.year,
            month=self.month,
            status='pending'
        ).count()
        
        total_overdue = MonthlyObligation.objects.filter(
            deadline__lt=timezone.now().date(),
            status='pending'
        ).count()
        
        self.stdout.write(f'\n📊 Συνολική κατάσταση {self.month}/{self.year}:')
        self.stdout.write(f'   • Εκκρεμούν: {total_pending}')
        
        if total_overdue > 0:
            self.stdout.write(self.style.WARNING(f'   • Καθυστερούν: {total_overdue}'))
        
        # Upcoming deadlines
        upcoming = MonthlyObligation.objects.filter(
            year=self.year,
            month=self.month,
            status='pending'
        ).order_by('deadline')[:5]
        
        if upcoming and self.verbose:
            self.stdout.write('\n📅 Προσεχείς προθεσμίες:')
            for obl in upcoming:
                days_left = (obl.deadline - timezone.now().date()).days
                if days_left < 0:
                    status = self.style.ERROR(f'ΚΑΘΥΣΤΕΡΕΙ {abs(days_left)}η')
                elif days_left == 0:
                    status = self.style.WARNING('ΣΗΜΕΡΑ')
                elif days_left <= 3:
                    status = self.style.WARNING(f'σε {days_left}η')
                else:
                    status = f'σε {days_left}η'
                
                self.stdout.write(
                    f'   • {obl.deadline.strftime("%d/%m")}: {obl.client.eponimia[:25]} '
                    f'- {obl.obligation_type.name[:20]} ({status})'
                )
        
        self.stdout.write('')
        self.stdout.write('=' * 70)
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🧪 DRY-RUN: Οι αλλαγές ΔΕΝ αποθηκεύτηκαν!'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Ολοκληρώθηκε επιτυχώς!'))
        
        self.stdout.write('')
    
    def send_report_email(self):
        """Send email report to admins"""
        if self.dry_run:
            self.stdout.write(self.style.WARNING('📧 Skip email (dry-run mode)'))
            return
        
        try:
            subject = f'[LogistikoCRM] Υποχρεώσεις {self.month}/{self.year} - Report'
            
            message = f"""
Καλησπέρα,

Ολοκληρώθηκε η δημιουργία υποχρεώσεων για {self.month}/{self.year}.

ΑΠΟΤΕΛΕΣΜΑΤΑ:
==============
✅ Δημιουργήθηκαν: {self.stats['created']} υποχρεώσεις
⏭️ Υπήρχαν ήδη: {self.stats['skipped']}
❌ Σφάλματα: {len(self.errors)}

ΣΤΑΤΙΣΤΙΚΑ:
===========
"""
            # Add type statistics
            for key, value in sorted(self.stats.items()):
                if key not in ['created', 'skipped'] and value > 0:
                    message += f"• {key}: {value}\n"
            
            # Add upcoming deadlines
            upcoming = MonthlyObligation.objects.filter(
                year=self.year,
                month=self.month,
                status='pending'
            ).order_by('deadline')[:10]
            
            if upcoming:
                message += "\n\nΠΡΟΣΕΧΕΙΣ ΠΡΟΘΕΣΜΙΕΣ:\n"
                message += "=" * 20 + "\n"
                for obl in upcoming:
                    message += f"• {obl.deadline.strftime('%d/%m/%Y')}: {obl.client.eponimia} - {obl.obligation_type.name}\n"
            
            message += f"""

Με εκτίμηση,
LogistikoCRM System
{timezone.now().strftime('%d/%m/%Y %H:%M')}
"""
            
            # Send email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin[1] for admin in settings.ADMINS],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('📧 Email report στάλθηκε!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'📧 Email failed: {str(e)}'))
            logger.error(f"Email sending failed: {str(e)}")
    
    def log_results(self):
        """Log results to file"""
        logger.info(
            f"Obligations generated for {self.month}/{self.year}: "
            f"Created={self.stats['created']}, Skipped={self.stats['skipped']}, "
            f"Errors={len(self.errors)}"
        )
        
        if self.errors:
            for error in self.errors:
                logger.error(f"Generation error: {error}")