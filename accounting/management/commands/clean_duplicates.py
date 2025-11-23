# accounting/management/commands/clean_duplicates.py

from django.core.management.base import BaseCommand
from django.db.models import Count, Min
from accounting.models import MonthlyObligation

class Command(BaseCommand):
    help = 'Καθαρισμός duplicate μηνιαίων υποχρεώσεων'
    
    def handle(self, *args, **kwargs):
        # Βρες duplicates
        duplicates = MonthlyObligation.objects.values(
            'client', 'obligation_type', 'year', 'month'
        ).annotate(
            count=Count('id'),
            first_id=Min('id')
        ).filter(count__gt=1)
        
        total_deleted = 0
        
        for dup in duplicates:
            # Κράτα την πρώτη (ή την ολοκληρωμένη αν υπάρχει)
            obligations = MonthlyObligation.objects.filter(
                client_id=dup['client'],
                obligation_type_id=dup['obligation_type'],
                year=dup['year'],
                month=dup['month']
            ).order_by('-status', 'id')  # Προτεραιότητα σε completed
            
            keep = obligations.first()
            to_delete = obligations.exclude(id=keep.id)
            
            if to_delete.exists():
                self.stdout.write(
                    f'  Διαγραφή {to_delete.count()} duplicates για '
                    f'{keep.client.eponimia} - {keep.obligation_type.name} ({keep.month}/{keep.year})'
                )
                total_deleted += to_delete.count()
                to_delete.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Διαγράφηκαν {total_deleted} duplicates!')
        )