from django.core.management.base import BaseCommand
from mydata.services import MyDataService


class Command(BaseCommand):
    help = 'Sync invoices from myDATA'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to sync back'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['received', 'transmitted', 'both'],
            default='both',
            help='Type of invoices to sync'
        )
    
    def handle(self, *args, **options):
        service = MyDataService()
        days = options['days']
        sync_type = options['type']
        
        self.stdout.write(f"🔍 Starting sync for last {days} days...")
        
        if sync_type in ['received', 'both']:
            self.stdout.write("\n📥 Syncing received invoices...")
            try:
                created, updated, errors = service.sync_received_invoices(days)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Received: {created} created, {updated} updated, {len(errors)} errors"
                    )
                )
                if errors:
                    for error in errors[:5]:  # Show first 5 errors
                        self.stdout.write(self.style.ERROR(f"  ❌ {error}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
        
        if sync_type in ['transmitted', 'both']:
            self.stdout.write("\n📤 Syncing transmitted invoices...")
            try:
                created, updated, errors = service.sync_transmitted_invoices(days)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Transmitted: {created} created, {updated} updated, {len(errors)} errors"
                    )
                )
                if errors:
                    for error in errors[:5]:
                        self.stdout.write(self.style.ERROR(f"  ❌ {error}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sync completed!'))