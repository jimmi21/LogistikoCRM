# Generated manually to remove unused Company.active field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_request_case'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='active',
        ),
    ]
