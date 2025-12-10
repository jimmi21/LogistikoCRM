# Generated manually for email improvements
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0026_bulk_scheduled_email_recipients'),
    ]

    operations = [
        # Add retry_count field to EmailLog
        migrations.AddField(
            model_name='emaillog',
            name='retry_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Αριθμός Επαναπροσπαθειών'),
        ),
        # Update status choices to include 'queued'
        migrations.AlterField(
            model_name='emaillog',
            name='status',
            field=models.CharField(
                choices=[
                    ('sent', 'Απεστάλη'),
                    ('failed', 'Αποτυχία'),
                    ('pending', 'Σε αναμονή'),
                    ('queued', 'Στην ουρά'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Κατάσταση',
            ),
        ),
    ]
