"""
Management command to create default email templates.

Usage:
    python manage.py create_email_templates
    python manage.py create_email_templates --force  # Recreate even if exists
"""

from django.core.management.base import BaseCommand
from accounting.models import EmailTemplate


class Command(BaseCommand):
    help = 'Δημιουργία βασικών email templates για το λογιστικό γραφείο'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Αντικατάσταση υπαρχόντων templates με το ίδιο όνομα',
        )

    def handle(self, *args, **options):
        force = options['force']

        templates = self.get_default_templates()

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for template_data in templates:
            name = template_data['name']
            existing = EmailTemplate.objects.filter(name=name).first()

            if existing:
                if force:
                    for key, value in template_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  Ενημερώθηκε: {name}')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.NOTICE(f'  Παραλείφθηκε (υπάρχει): {name}')
                    )
            else:
                EmailTemplate.objects.create(**template_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  Δημιουργήθηκε: {name}')
                )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Ολοκληρώθηκε! Δημιουργήθηκαν: {created_count}, '
                f'Ενημερώθηκαν: {updated_count}, Παραλείφθηκαν: {skipped_count}'
            )
        )

    def get_default_templates(self):
        """Return list of default email templates."""

        # Common HTML styles
        base_style = '''
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        '''

        footer = '''
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <p style="margin: 0; color: #666;">Με εκτίμηση,</p>
            <p style="margin: 5px 0 0 0; font-weight: 600; color: #333;">{accountant_name}</p>
            <p style="margin: 0; font-size: 14px; color: #666;">{company_name}</p>
        </div>
        </div>
        '''

        return [
            # 1. Ολοκλήρωση Υποχρέωσης
            {
                'name': 'Ολοκλήρωση Υποχρέωσης',
                'description': 'Ειδοποίηση πελάτη για ολοκλήρωση φορολογικής υποχρέωσης',
                'subject': 'Ολοκλήρωση {obligation_type} - Περίοδος {period_display}',
                'body_html': base_style + '''
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 25px; border-radius: 12px 12px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Ολοκλήρωση Υποχρέωσης</h1>
            </div>

            <div style="background: #f9fafb; padding: 25px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="font-size: 16px; margin-top: 0;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

                <p>Σας ενημερώνουμε ότι η υποχρέωση <strong>{obligation_type}</strong> για την περίοδο <strong>{period_display}</strong> ολοκληρώθηκε επιτυχώς.</p>

                <div style="background: white; border: 1px solid #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Τύπος:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{obligation_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Περίοδος:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{period_display}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Ημ/νία Ολοκλήρωσης:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{completed_date}</td>
                        </tr>
                    </table>
                </div>

                <p>Για οποιαδήποτε διευκρίνιση, μη διστάσετε να επικοινωνήσετε μαζί μας.</p>
                ''' + footer,
                'is_active': True,
            },

            # 2. Υπενθύμιση Προθεσμίας
            {
                'name': 'Υπενθύμιση Προθεσμίας',
                'description': 'Υπενθύμιση για επερχόμενη προθεσμία υποχρέωσης',
                'subject': 'Υπενθύμιση: {obligation_type} - Προθεσμία {deadline}',
                'body_html': base_style + '''
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 25px; border-radius: 12px 12px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Υπενθύμιση Προθεσμίας</h1>
            </div>

            <div style="background: #f9fafb; padding: 25px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="font-size: 16px; margin-top: 0;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

                <p>Σας υπενθυμίζουμε ότι πλησιάζει η προθεσμία για την υποχρέωση <strong>{obligation_type}</strong>.</p>

                <div style="background: white; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Τύπος:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{obligation_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Περίοδος:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{period_display}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Προθεσμία:</td>
                            <td style="padding: 8px 0; font-weight: 600; color: #d97706;">{deadline}</td>
                        </tr>
                    </table>
                </div>

                <p>Παρακαλούμε βεβαιωθείτε ότι έχετε αποστείλει όλα τα απαραίτητα στοιχεία εγκαίρως.</p>

                <p>Αν έχετε ήδη αποστείλει τα στοιχεία, παρακαλούμε αγνοήστε αυτό το μήνυμα.</p>
                ''' + footer,
                'is_active': True,
            },

            # 3. Εκπρόθεσμη Υποχρέωση
            {
                'name': 'Εκπρόθεσμη Υποχρέωση',
                'description': 'Ειδοποίηση για υποχρέωση που η προθεσμία έχει παρέλθει',
                'subject': 'Εκπρόθεσμη υποχρέωση: {obligation_type} - {period_display}',
                'body_html': base_style + '''
            <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 25px; border-radius: 12px 12px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Εκπρόθεσμη Υποχρέωση</h1>
            </div>

            <div style="background: #f9fafb; padding: 25px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="font-size: 16px; margin-top: 0;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

                <p>Σας ενημερώνουμε ότι η προθεσμία για την υποχρέωση <strong>{obligation_type}</strong> έχει παρέλθει.</p>

                <div style="background: white; border: 1px solid #fecaca; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Τύπος:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{obligation_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Περίοδος:</td>
                            <td style="padding: 8px 0; font-weight: 600;">{period_display}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Προθεσμία:</td>
                            <td style="padding: 8px 0; font-weight: 600; color: #dc2626;">{deadline}</td>
                        </tr>
                    </table>
                </div>

                <p><strong>Παρακαλούμε επικοινωνήστε μαζί μας άμεσα</strong> για να διευθετήσουμε την υποχρέωση και να αποφύγουμε πιθανά πρόστιμα.</p>
                ''' + footer,
                'is_active': True,
            },

            # 4. Αίτημα Εγγράφων
            {
                'name': 'Αίτημα Εγγράφων',
                'description': 'Αίτημα αποστολής εγγράφων/στοιχείων από τον πελάτη',
                'subject': 'Αίτημα στοιχείων για {obligation_type} - {period_display}',
                'body_html': base_style + '''
            <div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 25px; border-radius: 12px 12px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Αίτημα Στοιχείων</h1>
            </div>

            <div style="background: #f9fafb; padding: 25px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="font-size: 16px; margin-top: 0;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

                <p>Για την ολοκλήρωση της υποχρέωσης <strong>{obligation_type}</strong> (περίοδος {period_display}), παρακαλούμε να μας αποστείλετε τα παρακάτω στοιχεία:</p>

                <div style="background: white; border: 1px solid #c7d2fe; border-left: 4px solid #6366f1; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <ul style="margin: 0; padding-left: 20px; color: #374151;">
                        <li style="padding: 5px 0;">Παραστατικά εσόδων/εξόδων</li>
                        <li style="padding: 5px 0;">Αποδείξεις πληρωμών</li>
                        <li style="padding: 5px 0;">Τυχόν νέα συμβόλαια/συμφωνητικά</li>
                    </ul>
                </div>

                <div style="background: #fef3c7; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #92400e;">
                        <strong>Προθεσμία υποβολής:</strong> {deadline}
                    </p>
                </div>

                <p>Μπορείτε να στείλετε τα έγγραφα:</p>
                <ul style="color: #666;">
                    <li>Με email ως συνημμένα αρχεία</li>
                    <li>Μέσω του portal πελατών</li>
                    <li>Αυτοπροσώπως στο γραφείο μας</li>
                </ul>
                ''' + footer,
                'is_active': True,
            },

            # 5. Γενική Ενημέρωση
            {
                'name': 'Γενική Ενημέρωση',
                'description': 'Γενικό template για διάφορες ενημερώσεις',
                'subject': 'Ενημέρωση από {company_name}',
                'body_html': base_style + '''
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 25px; border-radius: 12px 12px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Ενημέρωση</h1>
            </div>

            <div style="background: #f9fafb; padding: 25px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="font-size: 16px; margin-top: 0;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

                <p>Σας ενημερώνουμε για τα εξής:</p>

                <div style="background: white; border: 1px solid #bfdbfe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <p style="margin: 0; color: #374151;">
                        [Εισάγετε το κείμενο της ενημέρωσης εδώ]
                    </p>
                </div>

                <p>Για οποιαδήποτε διευκρίνιση ή απορία, μη διστάσετε να επικοινωνήσετε μαζί μας.</p>
                ''' + footer,
                'is_active': True,
            },
        ]
