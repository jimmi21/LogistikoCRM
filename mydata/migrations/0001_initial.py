# Generated migration for mydata models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyDataCredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_encrypted_user_id', models.TextField(blank=True, default='', help_text='AADE User ID - κρυπτογραφημένο', verbose_name='User ID (encrypted)')),
                ('_encrypted_subscription_key', models.TextField(blank=True, default='', help_text='AADE Subscription Key - κρυπτογραφημένο', verbose_name='Subscription Key (encrypted)')),
                ('is_sandbox', models.BooleanField(default=False, help_text='True για testing environment (mydataapidev.aade.gr)', verbose_name='Sandbox Mode')),
                ('last_sync_at', models.DateTimeField(blank=True, null=True, verbose_name='Τελευταίο Sync')),
                ('last_vat_sync_at', models.DateTimeField(blank=True, null=True, verbose_name='Τελευταίο VAT Sync')),
                ('last_income_mark', models.BigIntegerField(default=0, help_text='Για incremental sync εσόδων', verbose_name='Τελευταίο Income Mark')),
                ('last_expense_mark', models.BigIntegerField(default=0, help_text='Για incremental sync εξόδων', verbose_name='Τελευταίο Expense Mark')),
                ('is_active', models.BooleanField(default=True, help_text='Αν είναι False, δεν θα γίνεται sync', verbose_name='Ενεργό')),
                ('is_verified', models.BooleanField(default=False, help_text='True αν τα credentials έχουν επιβεβαιωθεί', verbose_name='Επιβεβαιωμένο')),
                ('verification_error', models.TextField(blank=True, default='', help_text='Τελευταίο error message κατά την επιβεβαίωση', verbose_name='Σφάλμα Επιβεβαίωσης')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Δημιουργία')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ενημέρωση')),
                ('notes', models.TextField(blank=True, default='', help_text='Εσωτερικές σημειώσεις', verbose_name='Σημειώσεις')),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mydata_credentials', to='accounting.clientprofile', verbose_name='Πελάτης')),
            ],
            options={
                'verbose_name': 'myDATA Credentials',
                'verbose_name_plural': 'myDATA Credentials',
                'ordering': ['client__eponimia'],
            },
        ),
        migrations.CreateModel(
            name='VATRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.BigIntegerField(db_index=True, help_text='Μοναδικός αριθμός καταχώρησης myDATA', verbose_name='MARK')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Ακυρωμένο')),
                ('issue_date', models.DateField(db_index=True, verbose_name='Ημερομηνία Έκδοσης')),
                ('rec_type', models.IntegerField(choices=[(1, 'Εκροές (Έσοδα)'), (2, 'Εισροές (Έξοδα)')], db_index=True, help_text='1=Εκροές (έσοδα), 2=Εισροές (έξοδα)', verbose_name='Τύπος')),
                ('inv_type', models.CharField(db_index=True, help_text='π.χ. 1.1, 2.1, 5.1', max_length=10, verbose_name='Τύπος Παραστατικού')),
                ('vat_category', models.IntegerField(choices=[(1, 'ΦΠΑ 24%'), (2, 'ΦΠΑ 13%'), (3, 'ΦΠΑ 6%'), (4, 'ΦΠΑ 17%'), (5, 'ΦΠΑ 9%'), (6, 'ΦΠΑ 4%'), (7, 'ΦΠΑ 0%'), (8, 'Χωρίς ΦΠΑ')], db_index=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)], verbose_name='Κατηγορία ΦΠΑ')),
                ('vat_exemption_category', models.CharField(blank=True, default='', max_length=50, verbose_name='Κατηγορία Εξαίρεσης ΦΠΑ')),
                ('net_value', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Καθαρή Αξία')),
                ('vat_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Ποσό ΦΠΑ')),
                ('counter_vat_number', models.CharField(blank=True, db_index=True, default='', max_length=20, verbose_name='ΑΦΜ Αντισυμβαλλόμενου')),
                ('vat_offset_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Ποσό Συμψηφισμού ΦΠΑ')),
                ('deductions_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Ποσό Παρακρατήσεων')),
                ('fetched_at', models.DateTimeField(auto_now_add=True, help_text='Πότε τραβήχτηκε από το myDATA', verbose_name='Ημ/νία Λήψης')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ημ/νία Ενημέρωσης')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vat_records', to='accounting.clientprofile', verbose_name='Πελάτης')),
            ],
            options={
                'verbose_name': 'Εγγραφή ΦΠΑ',
                'verbose_name_plural': 'Εγγραφές ΦΠΑ',
                'ordering': ['-issue_date', '-mark'],
            },
        ),
        migrations.CreateModel(
            name='VATSyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sync_type', models.CharField(choices=[('VAT_INFO', 'VAT Info Sync'), ('INCOME', 'Income Sync'), ('EXPENSES', 'Expenses Sync'), ('VERIFY', 'Credentials Verification')], max_length=20, verbose_name='Τύπος Sync')),
                ('status', models.CharField(choices=[('PENDING', 'Σε εξέλιξη'), ('SUCCESS', 'Επιτυχία'), ('PARTIAL', 'Μερική επιτυχία'), ('ERROR', 'Σφάλμα')], default='PENDING', max_length=10, verbose_name='Κατάσταση')),
                ('date_from', models.DateField(blank=True, null=True, verbose_name='Από Ημερομηνία')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='Έως Ημερομηνία')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Έναρξη')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Ολοκλήρωση')),
                ('records_fetched', models.IntegerField(default=0, verbose_name='Εγγραφές που τραβήχτηκαν')),
                ('records_created', models.IntegerField(default=0, verbose_name='Νέες εγγραφές')),
                ('records_updated', models.IntegerField(default=0, verbose_name='Ενημερωμένες εγγραφές')),
                ('records_skipped', models.IntegerField(default=0, verbose_name='Παραλειφθείσες')),
                ('records_failed', models.IntegerField(default=0, verbose_name='Αποτυχίες')),
                ('error_message', models.TextField(blank=True, default='', verbose_name='Μήνυμα Σφάλματος')),
                ('details', models.JSONField(blank=True, help_text='Extra details σε JSON format', null=True, verbose_name='Λεπτομέρειες')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mydata_sync_logs', to='accounting.clientprofile', verbose_name='Πελάτης')),
            ],
            options={
                'verbose_name': 'VAT Sync Log',
                'verbose_name_plural': 'VAT Sync Logs',
                'ordering': ['-started_at'],
            },
        ),
        # Indexes for VATRecord
        migrations.AddIndex(
            model_name='vatrecord',
            index=models.Index(fields=['client', 'issue_date'], name='mydata_vatr_client__5c7a3f_idx'),
        ),
        migrations.AddIndex(
            model_name='vatrecord',
            index=models.Index(fields=['client', 'rec_type', 'issue_date'], name='mydata_vatr_client__f1f70e_idx'),
        ),
        migrations.AddIndex(
            model_name='vatrecord',
            index=models.Index(fields=['client', 'vat_category', 'issue_date'], name='mydata_vatr_client__7e6e08_idx'),
        ),
        migrations.AddIndex(
            model_name='vatrecord',
            index=models.Index(fields=['issue_date', 'rec_type'], name='mydata_vatr_issue_d_e2ce3c_idx'),
        ),
        # Unique constraint for VATRecord
        migrations.AddConstraint(
            model_name='vatrecord',
            constraint=models.UniqueConstraint(fields=['client', 'mark'], name='unique_client_mark'),
        ),
        # Indexes for VATSyncLog
        migrations.AddIndex(
            model_name='vatsynclog',
            index=models.Index(fields=['client', '-started_at'], name='mydata_vats_client__5e7a2b_idx'),
        ),
        migrations.AddIndex(
            model_name='vatsynclog',
            index=models.Index(fields=['sync_type', '-started_at'], name='mydata_vats_sync_ty_3c8b5a_idx'),
        ),
        migrations.AddIndex(
            model_name='vatsynclog',
            index=models.Index(fields=['status', '-started_at'], name='mydata_vats_status_8a4c2d_idx'),
        ),
    ]
