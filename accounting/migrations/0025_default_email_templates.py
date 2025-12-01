# Data migration to create default email templates

from django.db import migrations


def create_default_templates(apps, schema_editor):
    """Create default email templates for the CRM"""
    EmailTemplate = apps.get_model('accounting', 'EmailTemplate')

    # Template 1: Obligation Completion
    EmailTemplate.objects.get_or_create(
        name='Ολοκλήρωση Υποχρέωσης',
        defaults={
            'description': 'Αυτόματη ειδοποίηση όταν ολοκληρώνεται μια υποχρέωση',
            'subject': 'Ολοκλήρωση {obligation_type} - {period_display}',
            'body_html': '''<div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
        <h2 style="margin: 0;">Ολοκλήρωση Υποχρέωσης</h2>
    </div>

    <div style="background: #f8f9fa; padding: 25px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; color: #333;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

        <p style="color: #555; line-height: 1.6;">
            Σας ενημερώνουμε ότι η υποχρέωση <strong style="color: #667eea;">{obligation_type}</strong>
            για την περίοδο <strong>{period_display}</strong> ολοκληρώθηκε επιτυχώς στις <strong>{completed_date}</strong>.
        </p>

        <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0; color: #2e7d32;">
                <strong>Στοιχεία Υποχρέωσης:</strong><br>
                Τύπος: {obligation_type}<br>
                Περίοδος: {period_display}<br>
                Προθεσμία: {deadline}<br>
                Ημ/νία Ολοκλήρωσης: {completed_date}
            </p>
        </div>

        <p style="color: #555;">
            Παραμένουμε στη διάθεσή σας για οποιαδήποτε διευκρίνιση.
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">

        <p style="color: #333; margin-bottom: 5px;">Με εκτίμηση,</p>
        <p style="color: #667eea; font-weight: bold; margin: 0;">{accountant_name}</p>
        <p style="color: #888; font-size: 14px; margin: 5px 0;">{company_name}</p>
    </div>
</div>''',
            'is_active': True,
        }
    )

    # Template 2: General Notification
    EmailTemplate.objects.get_or_create(
        name='Γενική Ενημέρωση',
        defaults={
            'description': 'Γενικό πρότυπο για χειροκίνητα email',
            'subject': 'Ενημέρωση από {company_name}',
            'body_html': '''<div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #2196F3; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
        <h2 style="margin: 0;">Ενημέρωση</h2>
    </div>

    <div style="background: #f8f9fa; padding: 25px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; color: #333;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

        <p style="color: #555; line-height: 1.6;">
            Σας ενημερώνουμε για τα εξής:
        </p>

        <div style="background: white; padding: 15px; margin: 20px 0; border-radius: 8px; border: 1px solid #ddd;">
            <p style="margin: 0; color: #333;">
                [Το μήνυμά σας εδώ]
            </p>
        </div>

        <p style="color: #555;">
            Για οποιαδήποτε απορία, μη διστάσετε να επικοινωνήσετε μαζί μας.
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">

        <p style="color: #333; margin-bottom: 5px;">Με εκτίμηση,</p>
        <p style="color: #2196F3; font-weight: bold; margin: 0;">{accountant_name}</p>
        <p style="color: #888; font-size: 14px; margin: 5px 0;">{company_name}</p>
    </div>
</div>''',
            'is_active': True,
        }
    )

    # Template 3: Document Request
    EmailTemplate.objects.get_or_create(
        name='Υπενθύμιση Εγγράφων',
        defaults={
            'description': 'Αίτημα για υποβολή εγγράφων',
            'subject': 'Υπενθύμιση - Απαιτούμενα Έγγραφα για {obligation_type}',
            'body_html': '''<div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #ff9800; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
        <h2 style="margin: 0;">Υπενθύμιση Εγγράφων</h2>
    </div>

    <div style="background: #f8f9fa; padding: 25px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; color: #333;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

        <p style="color: #555; line-height: 1.6;">
            Σας υπενθυμίζουμε ότι για την ολοκλήρωση της υποχρέωσης
            <strong style="color: #ff9800;">{obligation_type}</strong> περιόδου <strong>{period_display}</strong>,
            χρειαζόμαστε τα παρακάτω έγγραφα:
        </p>

        <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0; color: #e65100;">
                <strong>Απαιτούμενα Έγγραφα:</strong><br>
                • [Έγγραφο 1]<br>
                • [Έγγραφο 2]<br>
                • [Έγγραφο 3]
            </p>
        </div>

        <div style="background: #ffebee; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; color: #c62828;">
                <strong>Προθεσμία:</strong> {deadline}
            </p>
        </div>

        <p style="color: #555;">
            Παρακαλούμε να μας αποστείλετε τα παραπάνω το συντομότερο δυνατό.
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">

        <p style="color: #333; margin-bottom: 5px;">Με εκτίμηση,</p>
        <p style="color: #ff9800; font-weight: bold; margin: 0;">{accountant_name}</p>
        <p style="color: #888; font-size: 14px; margin: 5px 0;">{company_name}</p>
    </div>
</div>''',
            'is_active': True,
        }
    )

    # Template 4: Deadline Reminder
    EmailTemplate.objects.get_or_create(
        name='Υπενθύμιση Προθεσμίας',
        defaults={
            'description': 'Υπενθύμιση για επερχόμενη προθεσμία',
            'subject': 'Υπενθύμιση Προθεσμίας - {obligation_type} ({deadline})',
            'body_html': '''<div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #f44336; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
        <h2 style="margin: 0;">Υπενθύμιση Προθεσμίας</h2>
    </div>

    <div style="background: #f8f9fa; padding: 25px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; color: #333;">Αγαπητέ/ή <strong>{client_name}</strong>,</p>

        <p style="color: #555; line-height: 1.6;">
            Σας υπενθυμίζουμε ότι η προθεσμία για την υποχρέωση
            <strong style="color: #f44336;">{obligation_type}</strong> περιόδου <strong>{period_display}</strong>
            πλησιάζει.
        </p>

        <div style="background: #ffebee; border: 2px solid #f44336; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center;">
            <p style="margin: 0; color: #c62828; font-size: 18px;">
                <strong>Προθεσμία: {deadline}</strong>
            </p>
        </div>

        <p style="color: #555;">
            Παρακαλούμε επικοινωνήστε μαζί μας για να διασφαλίσουμε την έγκαιρη υποβολή.
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">

        <p style="color: #333; margin-bottom: 5px;">Με εκτίμηση,</p>
        <p style="color: #f44336; font-weight: bold; margin: 0;">{accountant_name}</p>
        <p style="color: #888; font-size: 14px; margin: 5px 0;">{company_name}</p>
    </div>
</div>''',
            'is_active': True,
        }
    )


def reverse_migration(apps, schema_editor):
    """Remove default templates (optional)"""
    EmailTemplate = apps.get_model('accounting', 'EmailTemplate')
    EmailTemplate.objects.filter(
        name__in=[
            'Ολοκλήρωση Υποχρέωσης',
            'Γενική Ενημέρωση',
            'Υπενθύμιση Εγγράφων',
            'Υπενθύμιση Προθεσμίας',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0024_emailtemplate_obligation_type_emaillog'),
    ]

    operations = [
        migrations.RunPython(create_default_templates, reverse_migration),
    ]
