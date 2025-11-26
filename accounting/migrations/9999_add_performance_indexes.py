# Generated manually for performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0023_clientprofile_is_active_and_more'),  # Replace with latest
    ]

    operations = [
        # Add indexes to MonthlyObligation model (CRITICAL for dashboard performance)
        migrations.AddIndex(
            model_name='monthlyobligation',
            index=models.Index(fields=['status', 'deadline'], name='mo_status_deadline_idx'),
        ),
        migrations.AddIndex(
            model_name='monthlyobligation',
            index=models.Index(fields=['client', 'year', 'month'], name='mo_client_ym_idx'),
        ),
        migrations.AddIndex(
            model_name='monthlyobligation',
            index=models.Index(fields=['deadline', 'status'], name='mo_deadline_status_idx'),
        ),
        migrations.AddIndex(
            model_name='monthlyobligation',
            index=models.Index(fields=['-deadline'], name='mo_deadline_desc_idx'),
        ),
        migrations.AddIndex(
            model_name='monthlyobligation',
            index=models.Index(fields=['completed_by', 'completed_date'], name='mo_completed_idx'),
        ),
        
        # Add indexes to ClientProfile model
        migrations.AddIndex(
            model_name='clientprofile',
            index=models.Index(fields=['afm'], name='client_afm_idx'),
        ),
        migrations.AddIndex(
            model_name='clientprofile',
            index=models.Index(fields=['is_active', 'eponimia'], name='client_active_name_idx'),
        ),
        migrations.AddIndex(
            model_name='clientprofile',
            index=models.Index(fields=['company'], name='client_company_idx'),
        ),
        
        # Add indexes to VoIPCall model
        migrations.AddIndex(
            model_name='voipcall',
            index=models.Index(fields=['status', '-started_at'], name='voip_status_start_idx'),
        ),
        migrations.AddIndex(
            model_name='voipcall',
            index=models.Index(fields=['client', 'started_at'], name='voip_client_start_idx'),
        ),
        
        # Add indexes to Ticket model
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['status', 'priority'], name='ticket_status_prio_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['assigned_to', 'status'], name='ticket_assigned_idx'),
        ),
        
        # Add indexes to ScheduledEmail model
        migrations.AddIndex(
            model_name='scheduledemail',
            index=models.Index(fields=['status', 'send_at'], name='email_status_send_idx'),
        ),
        migrations.AddIndex(
            model_name='scheduledemail',
            index=models.Index(fields=['client', 'status'], name='email_client_status_idx'),
        ),
    ]
