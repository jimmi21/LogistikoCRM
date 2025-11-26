# Generated manually for performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),  # Replace with latest migration
    ]

    operations = [
        # Add indexes to Invoice model
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['issue_date', 'counterpart'], name='inv_issue_cpty_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['mydata_mark'], name='inv_mydata_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['is_outgoing', 'issue_date'], name='inv_outgoing_date_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['counterpart_vat'], name='inv_cpty_vat_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['-issue_date'], name='inv_date_desc_idx'),
        ),
        
        # Add indexes to StockMovement model
        migrations.AddIndex(
            model_name='stockmovement',
            index=models.Index(fields=['product', 'date'], name='stock_prod_date_idx'),
        ),
        migrations.AddIndex(
            model_name='stockmovement',
            index=models.Index(fields=['movement_type', 'date'], name='stock_type_date_idx'),
        ),
        migrations.AddIndex(
            model_name='stockmovement',
            index=models.Index(fields=['invoice'], name='stock_invoice_idx'),
        ),
        
        # Add indexes to Product model
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['active', 'code'], name='prod_active_code_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'active'], name='prod_cat_active_idx'),
        ),
    ]
