# Generated for unified document management system
# -*- coding: utf-8 -*-
"""
Migration: Ενοποιημένο Σύστημα Αρχειοθέτησης

Αλλαγές:
1. Προσθήκη νέων πεδίων στο ClientDocument:
   - original_filename, file_size
   - year, month (για filtering)
   - version, is_current, previous_version (versioning)
   - uploaded_by

2. Προσθήκη indexes για performance

3. Τα attachment/attachments στο MonthlyObligation παραμένουν ως deprecated
   (θα αφαιρεθούν σε μελλοντικό migration)
"""

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0027_add_emaillog_retry_count_and_queued_status'),
    ]

    operations = [
        # === ClientDocument: Νέα πεδία ===

        # original_filename
        migrations.AddField(
            model_name='clientdocument',
            name='original_filename',
            field=models.CharField(
                default='',
                help_text='Το όνομα του αρχείου όπως ανέβηκε',
                max_length=255,
                verbose_name='Αρχικό Όνομα'
            ),
            preserve_default=False,
        ),

        # file_size
        migrations.AddField(
            model_name='clientdocument',
            name='file_size',
            field=models.PositiveIntegerField(default=0, verbose_name='Μέγεθος (bytes)'),
        ),

        # year
        migrations.AddField(
            model_name='clientdocument',
            name='year',
            field=models.PositiveIntegerField(
                db_index=True,
                default=2025,
                help_text='Έτος αναφοράς (από υποχρέωση ή upload)',
                verbose_name='Έτος'
            ),
            preserve_default=False,
        ),

        # month
        migrations.AddField(
            model_name='clientdocument',
            name='month',
            field=models.PositiveIntegerField(
                db_index=True,
                default=1,
                help_text='Μήνας αναφοράς (από υποχρέωση ή upload)',
                verbose_name='Μήνας'
            ),
            preserve_default=False,
        ),

        # version
        migrations.AddField(
            model_name='clientdocument',
            name='version',
            field=models.PositiveIntegerField(default=1, verbose_name='Έκδοση'),
        ),

        # is_current
        migrations.AddField(
            model_name='clientdocument',
            name='is_current',
            field=models.BooleanField(db_index=True, default=True, verbose_name='Τρέχουσα Έκδοση'),
        ),

        # previous_version (self FK)
        migrations.AddField(
            model_name='clientdocument',
            name='previous_version',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='next_versions',
                to='accounting.clientdocument',
                verbose_name='Προηγούμενη Έκδοση'
            ),
        ),

        # uploaded_by
        migrations.AddField(
            model_name='clientdocument',
            name='uploaded_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='uploaded_documents',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Ανέβηκε από'
            ),
        ),

        # === Update existing fields ===

        # Update document_category choices (add apd, efka)
        migrations.AlterField(
            model_name='clientdocument',
            name='document_category',
            field=models.CharField(
                choices=[
                    ('contracts', 'Συμβάσεις'),
                    ('invoices', 'Τιμολόγια'),
                    ('tax', 'Φορολογικά'),
                    ('myf', 'ΜΥΦ'),
                    ('vat', 'ΦΠΑ'),
                    ('apd', 'ΑΠΔ'),
                    ('payroll', 'Μισθοδοσία'),
                    ('efka', 'ΕΦΚΑ'),
                    ('general', 'Γενικά'),
                ],
                db_index=True,
                default='general',
                max_length=20,
                verbose_name='Κατηγορία'
            ),
        ),

        # Update obligation related_name
        migrations.AlterField(
            model_name='clientdocument',
            name='obligation',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='documents',
                to='accounting.monthlyobligation',
                verbose_name='Υποχρέωση'
            ),
        ),

        # === Indexes for performance ===
        migrations.AddIndex(
            model_name='clientdocument',
            index=models.Index(
                fields=['client', 'year', 'month'],
                name='accounting__client__b1c2a3_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='clientdocument',
            index=models.Index(
                fields=['client', 'document_category'],
                name='accounting__client__d4e5f6_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='clientdocument',
            index=models.Index(
                fields=['obligation', 'is_current'],
                name='accounting__obligat__g7h8i9_idx'
            ),
        ),

        # === Mark MonthlyObligation fields as deprecated ===
        migrations.AlterField(
            model_name='monthlyobligation',
            name='attachment',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='deprecated/',
                verbose_name='[DEPRECATED] Συνημμένο Αρχείο',
                help_text='Χρησιμοποιήστε ClientDocument αντί αυτού'
            ),
        ),
        migrations.AlterField(
            model_name='monthlyobligation',
            name='attachments',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='[DEPRECATED] List of attachment paths - use ClientDocument'
            ),
        ),
    ]
