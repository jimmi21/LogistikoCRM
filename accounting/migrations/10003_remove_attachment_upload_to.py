# Generated manually - ArchiveService refactoring
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '10002_ticket_call_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlyobligation',
            name='attachment',
            field=models.FileField(
                blank=True,
                null=True,
                verbose_name='Συνημμένο Αρχείο',
                help_text='Κύριο αρχείο υποχρέωσης. Αποθηκεύεται μέσω ArchiveService.'
            ),
        ),
    ]
