# Generated manually for ticket-call deletion management

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '10001_remove_clientprofile_client_afm_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='call',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ticket',
                to='accounting.voipcall',
                verbose_name='Κλήση',
            ),
        ),
    ]
