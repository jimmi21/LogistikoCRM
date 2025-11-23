from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from accounting.models import MonthlyObligation
from datetime import timedelta


class Command(BaseCommand):
    help = 'Αποστολή ημερήσιας αναφοράς υποχρεώσεων'

    def add_arguments(self, parser):
        parser.add_argument(
            '--emails',
            nargs='+',
            type=str,
            help='Email παραληπτών (default: ADMINS από settings)',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        upcoming_deadline = today + timedelta(days=5)
        
        # Καθυστερημένες
        overdue = MonthlyObligation.objects.filter(
            status__in=['pending', 'overdue'],
            deadline__lt=today
        ).select_related('client', 'obligation_type').order_by('deadline')
        
        # Επερχόμενες (επόμενες 5 ημέρες)
        upcoming = MonthlyObligation.objects.filter(
            status='pending',
            deadline__gte=today,
            deadline__lte=upcoming_deadline
        ).select_related('client', 'obligation_type').order_by('deadline')
        
        # Αν δεν υπάρχουν, μην στείλεις email
        if not overdue.exists() and not upcoming.exists():
            self.stdout.write(self.style.SUCCESS('✅ Δεν υπάρχουν υποχρεώσεις για ειδοποίηση'))
            return
        
        # Δημιουργία email body
        subject = f'📋 Ημερήσια Αναφορά Υποχρεώσεων - {today.strftime("%d/%m/%Y")}'
        
        body = f"""
Καλημέρα,

Ημερήσια αναφορά υποχρεώσεων για {today.strftime("%d/%m/%Y")}:

"""
        
        # Καθυστερημένες
        if overdue.exists():
            body += f"""
🔴 ΚΑΘΥΣΤΕΡΗΜΕΝΕΣ ΥΠΟΧΡΕΩΣΕΙΣ ({overdue.count()}):
{'='*60}
"""
            for obl in overdue:
                days_overdue = (today - obl.deadline).days
                body += f"""
- {obl.client.eponimia} ({obl.client.afm})
  └─ {obl.obligation_type.name}
  └─ Προθεσμία: {obl.deadline.strftime('%d/%m/%Y')} (Καθυστερεί {days_overdue} ημέρες)

"""
        
        # Επερχόμενες
        if upcoming.exists():
            body += f"""

🟡 ΕΠΕΡΧΟΜΕΝΕΣ ΥΠΟΧΡΕΩΣΕΙΣ (Επόμενες 5 ημέρες - {upcoming.count()}):
{'='*60}
"""
            for obl in upcoming:
                days_until = obl.days_until_deadline
                body += f"""
- {obl.client.eponimia} ({obl.client.afm})
  └─ {obl.obligation_type.name}
  └─ Προθεσμία: {obl.deadline.strftime('%d/%m/%Y')} (Σε {days_until} ημέρες)

"""
        
        body += f"""

Για περισσότερες λεπτομέρειες, επισκεφθείτε το Dashboard:
{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'}/accounting/dashboard/

---
Αυτόματο μήνυμα από το Σύστημα Διαχείρισης Υποχρεώσεων
"""
        
        # Προσδιορισμός παραληπτών
        recipients = options.get('emails')
        if not recipients:
            recipients = [admin[1] for admin in settings.ADMINS]
        
        if not recipients:
            self.stdout.write(self.style.ERROR('❌ Δεν βρέθηκαν email παραλήπτες!'))
            return
        
        # Αποστολή
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(
                f'✅ Email στάλθηκε επιτυχώς σε: {", ".join(recipients)}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Σφάλμα αποστολής: {str(e)}'))