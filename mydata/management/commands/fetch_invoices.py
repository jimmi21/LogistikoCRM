"""
Django management command: python manage.py fetch_invoices
Fetches invoices from myDATA and imports them into the database
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from mydata.client import MyDataClient
from inventory.models import Invoice, InvoiceItem
from accounting.models import ClientProfile
from datetime import datetime, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fetch invoices from myDATA and import into database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to fetch (default: 365)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("📥 Λήψη Τιμολογίων από myDATA"))
        self.stdout.write("=" * 60)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - Δεν θα αποθηκευτούν δεδομένα"))
        
        # Initialize myDATA client
        client = MyDataClient(
            user_id=settings.MYDATA_USER_ID,
            subscription_key=settings.MYDATA_SUBSCRIPTION_KEY,
            is_sandbox=settings.MYDATA_IS_SANDBOX
        )
        
        # Date range
        date_from = datetime.now() - timedelta(days=days)
        date_to = datetime.now()
        
        self.stdout.write(f"\n📅 Χρονικό Διάστημα: {date_from.date()} έως {date_to.date()}")
        self.stdout.write(f"🌍 Περιβάλλον: {'SANDBOX (Test)' if settings.MYDATA_IS_SANDBOX else 'PRODUCTION'}")
        self.stdout.write("\n⏳ Λήψη τιμολογίων από API...")
        
        try:
            # Fetch from myDATA
            response = client.request_docs(date_from=date_from, date_to=date_to)
            invoices = client.parse_invoice_response(response)
            
            self.stdout.write(self.style.SUCCESS(f"\n✅ Βρέθηκαν {len(invoices)} τιμολόγια στο myDATA"))
            
            if len(invoices) == 0:
                self.stdout.write(self.style.WARNING("💡 Δεν βρέθηκαν τιμολόγια στο διάστημα"))
                return
            
            # Import stats
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            for inv_data in invoices:
                try:
                    # Supplier info
                    supplier_vat = inv_data.get('issuer_vat')
                    if not supplier_vat:
                        self.stdout.write(self.style.WARNING(f"⚠️  Παράλειψη - χωρίς ΑΦΜ προμηθευτή"))
                        skipped_count += 1
                        continue
                    
                    # Invoice details
                    series = inv_data.get('series', 'A')
                    number = inv_data.get('aa', '')
                    
                    # Check if exists
                    if Invoice.objects.filter(series=series, number=number).exists():
                        self.stdout.write(f"  ⏭️  {series}/{number} υπάρχει ήδη")
                        skipped_count += 1
                        continue
                    
                    if dry_run:
                        self.stdout.write(f"  📋 Θα εισάγω: {series}/{number} - {supplier_vat} - €{inv_data.get('total_gross', 0)}")
                        imported_count += 1
                        continue
                    
                    # Get or create supplier in ClientProfile
                    try:
                        counterpart = ClientProfile.objects.get(afm=supplier_vat)
                    except ClientProfile.DoesNotExist:
                        # Δημιουργία νέου προμηθευτή
                        counterpart = ClientProfile.objects.create(
                            afm=supplier_vat,
                            eponimia=f'Συναλλασσόμενος ΑΦΜ: {supplier_vat}',
                            doy='ΑΘΗΝΩΝ'  # Default
                        )
                        self.stdout.write(self.style.SUCCESS(f"    ✨ Δημιουργήθηκε νέος: {supplier_vat}"))
                    except ClientProfile.MultipleObjectsReturned:
                        counterpart = ClientProfile.objects.filter(afm=supplier_vat).first()
                    
                    # Parse date
                    issue_date_str = inv_data.get('issue_date', '')
                    try:
                        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
                    except:
                        issue_date = timezone.now().date()
                    
                    # Create invoice (INCOMING)
                    invoice = Invoice.objects.create(
                        series=series,
                        number=number,
                        invoice_type=inv_data.get('invoice_type', '2.1'),
                        issue_date=issue_date,
                        counterpart=counterpart,
                        counterpart_vat=supplier_vat,
                        counterpart_name=f"Προμηθευτής {supplier_vat}",
                        is_outgoing=False,  # INCOMING invoice!
                        total_net=Decimal(str(inv_data.get('total_net', 0))),
                        total_vat=Decimal(str(inv_data.get('total_vat', 0))),
                        total_gross=Decimal(str(inv_data.get('total_gross', 0))),
                        mydata_mark=inv_data.get('mark') or None,
                        mydata_uid=inv_data.get('uid') or '',
                        mydata_sent=True,
                        mydata_sent_at=timezone.now(),
                        notes=f"Εισαγωγή από myDATA - ΑΦΜ Πελάτη: {inv_data.get('counterpart_vat', '')}"
                    )
                    
                    # Create invoice item (summary)
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        line_number=1,
                        description="Εισαγωγή από myDATA",
                        quantity=Decimal('1'),
                        unit='piece',
                        unit_price=invoice.total_net,
                        net_value=invoice.total_net,
                        vat_category=1,  # Default 24%
                        vat_amount=invoice.total_vat
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✅ Εισήχθη: {series}/{number} - {supplier_vat} - €{invoice.total_gross}"
                    ))
                    imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Σφάλμα: {e}"))
                    error_count += 1
                    continue
            
            # Summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ Ολοκληρώθηκε η Εισαγωγή!"))
            self.stdout.write(f"   Εισήχθησαν: {imported_count}")
            self.stdout.write(f"   Παραλείφθηκαν: {skipped_count}")
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f"   Σφάλματα: {error_count}"))
            self.stdout.write(f"   Σύνολο στη βάση: {Invoice.objects.filter(is_outgoing=False).count()} εισερχόμενα")
            self.stdout.write("=" * 60)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Σφάλμα λήψης: {e}"))
            import traceback
            traceback.print_exc()