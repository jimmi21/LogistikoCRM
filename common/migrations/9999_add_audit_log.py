# Generated manually for audit trail system
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0004_alter_reminder_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=150)),
                ('action', models.CharField(choices=[('create', 'Created'), ('update', 'Updated'), ('delete', 'Deleted'), ('view', 'Viewed'), ('export', 'Exported'), ('login', 'Login'), ('logout', 'Logout'), ('failed_login', 'Failed Login'), ('permission_denied', 'Permission Denied')], db_index=True, max_length=20)),
                ('model_name', models.CharField(db_index=True, max_length=100)),
                ('object_id', models.CharField(blank=True, max_length=255)),
                ('object_repr', models.CharField(blank=True, max_length=255)),
                ('changes', models.JSONField(blank=True, default=dict)),
                ('description', models.TextField(blank=True)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], db_index=True, default='low', max_length=10)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('extra_data', models.JSONField(blank=True, default=dict)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Log Entry',
                'verbose_name_plural': 'Audit Log',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['-timestamp', 'user'], name='common_audi_timesta_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['model_name', 'action'], name='common_audi_model_n_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['severity', '-timestamp'], name='common_audi_severit_idx'),
        ),
    ]
