# Generated manually
# accounting/migrations/10004_document_sharing_system.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def generate_share_token():
    import secrets
    return secrets.token_urlsafe(32)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '10003_obligationtype_profile_to_profiles'),
    ]

    operations = [
        # DocumentTag model
        migrations.CreateModel(
            name='DocumentTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Όνομα')),
                ('color', models.CharField(default='#3B82F6', help_text='Hex color code (π.χ. #3B82F6)', max_length=7, verbose_name='Χρώμα')),
                ('icon', models.CharField(blank=True, help_text='Lucide icon name (π.χ. file-text)', max_length=50, verbose_name='Εικονίδιο')),
                ('description', models.TextField(blank=True, verbose_name='Περιγραφή')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tags', to=settings.AUTH_USER_MODEL, verbose_name='Δημιουργήθηκε από')),
            ],
            options={
                'verbose_name': 'Ετικέτα Εγγράφου',
                'verbose_name_plural': 'Ετικέτες Εγγράφων',
                'ordering': ['name'],
            },
        ),
        # DocumentTagAssignment model
        migrations.CreateModel(
            name='DocumentTagAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tag_assignments', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_assignments', to='accounting.clientdocument')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_assignments', to='accounting.documenttag')),
            ],
            options={
                'verbose_name': 'Ανάθεση Ετικέτας',
                'verbose_name_plural': 'Αναθέσεις Ετικετών',
                'ordering': ['-assigned_at'],
                'unique_together': {('document', 'tag')},
            },
        ),
        # SharedLink model
        migrations.CreateModel(
            name='SharedLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=generate_share_token, max_length=64, unique=True, verbose_name='Token')),
                ('name', models.CharField(blank=True, help_text='Φιλικό όνομα για αναγνώριση', max_length=255, verbose_name='Όνομα Συνδέσμου')),
                ('access_level', models.CharField(choices=[('view', 'Μόνο προβολή'), ('download', 'Προβολή & Λήψη')], default='download', max_length=20, verbose_name='Επίπεδο Πρόσβασης')),
                ('password_hash', models.CharField(blank=True, max_length=128, verbose_name='Κωδικός (hashed)')),
                ('requires_email', models.BooleanField(default=False, help_text='Ο χρήστης πρέπει να εισάγει email για πρόσβαση', verbose_name='Απαιτεί Email')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Αν είναι κενό, δεν λήγει', null=True, verbose_name='Λήξη')),
                ('max_downloads', models.PositiveIntegerField(blank=True, help_text='Αν είναι κενό, απεριόριστες', null=True, verbose_name='Μέγιστες Λήψεις')),
                ('download_count', models.PositiveIntegerField(default=0, verbose_name='Πλήθος Λήψεων')),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='Πλήθος Προβολών')),
                ('last_accessed_at', models.DateTimeField(blank=True, null=True, verbose_name='Τελευταία Πρόσβαση')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ενεργό')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shared_folder_links', to='accounting.clientprofile', verbose_name='Φάκελος Πελάτη')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_shared_links', to=settings.AUTH_USER_MODEL, verbose_name='Δημιουργήθηκε από')),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shared_links', to='accounting.clientdocument', verbose_name='Έγγραφο')),
            ],
            options={
                'verbose_name': 'Κοινόχρηστος Σύνδεσμος',
                'verbose_name_plural': 'Κοινόχρηστοι Σύνδεσμοι',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='sharedlink',
            index=models.Index(fields=['token'], name='accounting__token_4ab5c3_idx'),
        ),
        migrations.AddIndex(
            model_name='sharedlink',
            index=models.Index(fields=['is_active', 'expires_at'], name='accounting__is_acti_a2b3c4_idx'),
        ),
        # SharedLinkAccess model
        migrations.CreateModel(
            name='SharedLinkAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accessed_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Διεύθυνση')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('email_provided', models.EmailField(blank=True, max_length=254, verbose_name='Email που δόθηκε')),
                ('action', models.CharField(choices=[('view', 'Προβολή'), ('download', 'Λήψη')], default='view', max_length=20, verbose_name='Ενέργεια')),
                ('shared_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_logs', to='accounting.sharedlink')),
            ],
            options={
                'verbose_name': 'Πρόσβαση Συνδέσμου',
                'verbose_name_plural': 'Προσβάσεις Συνδέσμων',
                'ordering': ['-accessed_at'],
            },
        ),
        # DocumentFavorite model
        migrations.CreateModel(
            name='DocumentFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.CharField(blank=True, max_length=255, verbose_name='Σημείωση')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='accounting.clientdocument')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Αγαπημένο Έγγραφο',
                'verbose_name_plural': 'Αγαπημένα Έγγραφα',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'document')},
            },
        ),
        # DocumentCollection model
        migrations.CreateModel(
            name='DocumentCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Όνομα')),
                ('description', models.TextField(blank=True, verbose_name='Περιγραφή')),
                ('color', models.CharField(default='#6366F1', max_length=7, verbose_name='Χρώμα')),
                ('icon', models.CharField(default='folder', max_length=50, verbose_name='Εικονίδιο')),
                ('is_shared', models.BooleanField(default=False, help_text='Ορατό σε όλους τους χρήστες', verbose_name='Κοινόχρηστο')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('documents', models.ManyToManyField(blank=True, related_name='collections', to='accounting.clientdocument', verbose_name='Έγγραφα')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_collections', to=settings.AUTH_USER_MODEL, verbose_name='Ιδιοκτήτης')),
            ],
            options={
                'verbose_name': 'Συλλογή Εγγράφων',
                'verbose_name_plural': 'Συλλογές Εγγράφων',
                'ordering': ['name'],
            },
        ),
    ]
