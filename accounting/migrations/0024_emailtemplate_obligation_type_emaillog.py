# Generated migration for email system enhancements

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0023_clientprofile_is_active_and_more'),
    ]

    operations = [
        # Add obligation_type FK to EmailTemplate
        migrations.AddField(
            model_name='emailtemplate',
            name='obligation_type',
            field=models.ForeignKey(
                blank=True,
                help_text='Αν οριστεί, αυτό το template επιλέγεται αυτόματα για αυτόν τον τύπο υποχρέωσης',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='accounting.obligationtype',
                verbose_name='Τύπος Υποχρέωσης (αυτόματη επιλογή)',
            ),
        ),
        # Create EmailLog model
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_email', models.EmailField(max_length=254, verbose_name='Email Παραλήπτη')),
                ('recipient_name', models.CharField(max_length=200, verbose_name='Όνομα Παραλήπτη')),
                ('subject', models.CharField(max_length=500, verbose_name='Θέμα')),
                ('body', models.TextField(verbose_name='Κείμενο')),
                ('status', models.CharField(
                    choices=[('sent', 'Απεστάλη'), ('failed', 'Αποτυχία'), ('pending', 'Σε αναμονή')],
                    default='pending',
                    max_length=20,
                    verbose_name='Κατάσταση',
                )),
                ('error_message', models.TextField(blank=True, verbose_name='Μήνυμα Σφάλματος')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Αποστολή')),
                ('client', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='email_logs',
                    to='accounting.clientprofile',
                    verbose_name='Πελάτης',
                )),
                ('obligation', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='email_logs',
                    to='accounting.monthlyobligation',
                    verbose_name='Υποχρέωση',
                )),
                ('sent_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sent_emails',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Αποστολέας',
                )),
                ('template_used', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='accounting.emailtemplate',
                    verbose_name='Πρότυπο',
                )),
            ],
            options={
                'verbose_name': 'Ιστορικό Email',
                'verbose_name_plural': 'Ιστορικό Email',
                'ordering': ['-sent_at'],
            },
        ),
        # Add indexes for EmailLog
        migrations.AddIndex(
            model_name='emaillog',
            index=models.Index(fields=['client', '-sent_at'], name='accounting__client__7d2cc2_idx'),
        ),
        migrations.AddIndex(
            model_name='emaillog',
            index=models.Index(fields=['status', '-sent_at'], name='accounting__status_3f4dc1_idx'),
        ),
        migrations.AddIndex(
            model_name='emaillog',
            index=models.Index(fields=['-sent_at'], name='accounting__sent_at_a6b9c2_idx'),
        ),
    ]
