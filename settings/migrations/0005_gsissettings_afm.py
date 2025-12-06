# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0004_gsissettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='gsissettings',
            name='afm',
            field=models.CharField(
                default='000000000',
                help_text='Το ΑΦΜ του λογιστή (για την παράμετρο afm_called_by)',
                max_length=9,
                verbose_name='ΑΦΜ'
            ),
            preserve_default=False,
        ),
    ]
