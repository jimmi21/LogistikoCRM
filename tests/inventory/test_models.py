"""
Comprehensive tests for Inventory app models
Tests for: Product, StockMovement, Invoice, InvoiceItem, MyDataSyncLog
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from inventory.models import (
    ProductCategory, Product, StockMovement, Invoice, InvoiceItem,
    MyDataSyncLog
)
from accounting.models import ClientProfile


class ProductCategoryModelTest(TestCase):
    """Test ProductCategory model"""

    def test_create_category(self):
        """Test creating a product category"""
        category = ProductCategory.objects.create(
            name="Ξυλεία Καστανιάς",
            description="Ξυλεία από καστανιά"
        )

        self.assertEqual(category.name, "Ξυλεία Καστανιάς")
        self.assertEqual(str(category), "Ξυλεία Καστανιάς")

    def test_category_with_parent(self):
        """Test creating subcategory"""
        parent = ProductCategory.objects.create(
            name="Ξυλεία"
        )

        child = ProductCategory.objects.create(
            name="Καστανιά",
            parent=parent
        )

        self.assertEqual(child.parent, parent)


class ProductModelTest(TestCase):
    """Test Product model"""

    def setUp(self):
        self.category = ProductCategory.objects.create(
            name="Ξυλεία"
        )

    def test_create_product(self):
        """Test creating a product"""
        product = Product.objects.create(
            code="WOOD001",
            name="Ξυλεία Καστανιάς 2m",
            category=self.category,
            unit="m3",
            current_stock=Decimal('100.000'),
            min_stock=Decimal('10.000'),
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('75.00'),
            vat_category=1  # 24%
        )

        self.assertEqual(product.code, "WOOD001")
        self.assertEqual(product.name, "Ξυλεία Καστανιάς 2m")
        self.assertEqual(product.current_stock, Decimal('100.000'))
        self.assertTrue(product.active)
        self.assertEqual(str(product), "WOOD001 - Ξυλεία Καστανιάς 2m")

    def test_product_unique_code(self):
        """Test that product code must be unique"""
        Product.objects.create(
            code="PROD001",
            name="Product 1",
            unit="piece",
            sale_price=Decimal('10.00')
        )

        with self.assertRaises(Exception):
            Product.objects.create(
                code="PROD001",  # Duplicate
                name="Product 2",
                unit="piece",
                sale_price=Decimal('20.00')
            )

    def test_product_is_low_stock(self):
        """Test low stock detection"""
        product = Product.objects.create(
            code="PROD002",
            name="Test Product",
            unit="piece",
            current_stock=Decimal('5.000'),
            min_stock=Decimal('10.000'),
            sale_price=Decimal('10.00')
        )

        self.assertTrue(product.is_low_stock)

        # Increase stock
        product.current_stock = Decimal('15.000')
        product.save()

        self.assertFalse(product.is_low_stock)

    def test_product_stock_value(self):
        """Test stock value calculation"""
        product = Product.objects.create(
            code="PROD003",
            name="Test Product",
            unit="piece",
            current_stock=Decimal('100.000'),
            purchase_price=Decimal('25.50'),
            sale_price=Decimal('40.00')
        )

        expected_value = Decimal('100.000') * Decimal('25.50')
        self.assertEqual(product.stock_value, expected_value)

    def test_product_get_vat_rate(self):
        """Test VAT rate retrieval"""
        product = Product.objects.create(
            code="PROD004",
            name="Test Product",
            unit="piece",
            sale_price=Decimal('10.00'),
            vat_category=1  # 24%
        )

        self.assertEqual(product.get_vat_rate(), 24)

        product.vat_category = 2  # 13%
        self.assertEqual(product.get_vat_rate(), 13)

        product.vat_category = 7  # No VAT
        self.assertEqual(product.get_vat_rate(), 0)


class StockMovementModelTest(TestCase):
    """Test StockMovement model and stock tracking"""

    def setUp(self):
        self.product = Product.objects.create(
            code="PROD001",
            name="Test Product",
            unit="piece",
            current_stock=Decimal('50.000'),
            sale_price=Decimal('10.00')
        )

        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Supplier",
            eidos_ipoxreou="company"
        )

    def test_create_stock_movement_in(self):
        """Test creating an incoming stock movement"""
        initial_stock = self.product.current_stock

        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='IN',
            quantity=Decimal('25.000'),
            unit_cost=Decimal('8.00'),
            counterpart=self.client,
            notes="Incoming delivery"
        )

        # Refresh product
        self.product.refresh_from_db()

        # Stock should increase
        expected_stock = initial_stock + Decimal('25.000')
        self.assertEqual(self.product.current_stock, expected_stock)
        self.assertEqual(movement.total_value, Decimal('200.00'))

    def test_create_stock_movement_out(self):
        """Test creating an outgoing stock movement"""
        initial_stock = self.product.current_stock

        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='OUT',
            quantity=Decimal('10.000'),
            counterpart=self.client,
            notes="Sale"
        )

        # Refresh product
        self.product.refresh_from_db()

        # Stock should decrease
        expected_stock = initial_stock - Decimal('10.000')
        self.assertEqual(self.product.current_stock, expected_stock)

    def test_create_stock_movement_adjustment(self):
        """Test stock adjustment"""
        initial_stock = self.product.current_stock

        # Positive adjustment
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='ADJ',
            quantity=Decimal('5.000'),
            notes="Inventory correction"
        )

        self.product.refresh_from_db()
        expected_stock = initial_stock + Decimal('5.000')
        self.assertEqual(self.product.current_stock, expected_stock)

    def test_stock_movement_string_representation(self):
        """Test stock movement str()"""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='IN',
            quantity=Decimal('10.000')
        )

        self.assertIn('Εισαγωγή', str(movement))
        self.assertIn('PROD001', str(movement))
        self.assertIn('10', str(movement))

    def test_stock_movement_update_modifies_stock(self):
        """Test that updating a movement adjusts stock correctly"""
        # Create initial movement
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='IN',
            quantity=Decimal('20.000')
        )

        self.product.refresh_from_db()
        stock_after_first = self.product.current_stock

        # Modify the movement
        movement.quantity = Decimal('30.000')
        movement.save()

        self.product.refresh_from_db()

        # Stock should reflect the change (+10 more)
        self.assertEqual(
            self.product.current_stock,
            stock_after_first + Decimal('10.000')
        )


class InvoiceModelTest(TestCase):
    """Test Invoice model"""

    def setUp(self):
        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Client Ltd",
            eidos_ipoxreou="company"
        )

    def test_create_invoice(self):
        """Test creating an invoice"""
        invoice = Invoice.objects.create(
            series="A",
            number="001",
            invoice_type="1.1",
            issue_date=datetime(2024, 3, 15).date(),
            counterpart=self.client,
            counterpart_vat=self.client.afm,
            counterpart_name=self.client.eponimia,
            is_outgoing=True,
            total_net=Decimal('100.00'),
            total_vat=Decimal('24.00'),
            total_gross=Decimal('124.00')
        )

        self.assertEqual(invoice.series, "A")
        self.assertEqual(invoice.number, "001")
        self.assertEqual(invoice.total_gross, Decimal('124.00'))
        self.assertFalse(invoice.mydata_sent)
        self.assertIn("A/001", str(invoice))

    def test_invoice_unique_series_number(self):
        """Test that series+number must be unique"""
        Invoice.objects.create(
            series="A",
            number="001",
            invoice_type="1.1",
            counterpart=self.client,
            counterpart_vat=self.client.afm,
            counterpart_name=self.client.eponimia,
            is_outgoing=True
        )

        with self.assertRaises(Exception):
            Invoice.objects.create(
                series="A",
                number="001",  # Duplicate
                invoice_type="1.1",
                counterpart=self.client,
                counterpart_vat=self.client.afm,
                counterpart_name=self.client.eponimia,
                is_outgoing=True
            )

    def test_invoice_calculate_totals(self):
        """Test invoice totals calculation from items"""
        product = Product.objects.create(
            code="PROD001",
            name="Test Product",
            unit="piece",
            sale_price=Decimal('50.00'),
            vat_category=1  # 24%
        )

        invoice = Invoice.objects.create(
            series="A",
            number="002",
            invoice_type="1.1",
            counterpart=self.client,
            counterpart_vat=self.client.afm,
            counterpart_name=self.client.eponimia,
            is_outgoing=True
        )

        # Add items
        InvoiceItem.objects.create(
            invoice=invoice,
            line_number=1,
            product=product,
            description="Product 1",
            quantity=Decimal('2.000'),
            unit="piece",
            unit_price=Decimal('50.00'),
            vat_category=1
        )

        InvoiceItem.objects.create(
            invoice=invoice,
            line_number=2,
            description="Product 2",
            quantity=Decimal('1.000'),
            unit="piece",
            unit_price=Decimal('30.00'),
            vat_category=1
        )

        # Recalculate totals
        invoice.calculate_totals()

        # Total net: 100 + 30 = 130
        # Total VAT: 24 + 7.20 = 31.20
        # Total gross: 161.20
        self.assertEqual(invoice.total_net, Decimal('130.00'))
        self.assertEqual(invoice.total_vat, Decimal('31.20'))
        self.assertEqual(invoice.total_gross, Decimal('161.20'))

    def test_invoice_mydata_fields(self):
        """Test myDATA integration fields"""
        invoice = Invoice.objects.create(
            series="A",
            number="003",
            invoice_type="1.1",
            counterpart=self.client,
            counterpart_vat=self.client.afm,
            counterpart_name=self.client.eponimia,
            is_outgoing=True
        )

        # Initially not sent
        self.assertFalse(invoice.mydata_sent)
        self.assertIsNone(invoice.mydata_mark)
        self.assertEqual(invoice.mydata_uid, "")

        # Mark as sent
        invoice.mydata_sent = True
        invoice.mydata_mark = 123456789
        invoice.mydata_uid = "ABC123XYZ"
        invoice.mydata_sent_at = timezone.now()
        invoice.save()

        self.assertTrue(invoice.mydata_sent)
        self.assertEqual(invoice.mydata_mark, 123456789)
        self.assertIsNotNone(invoice.mydata_sent_at)


class InvoiceItemModelTest(TestCase):
    """Test InvoiceItem model"""

    def setUp(self):
        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Client",
            eidos_ipoxreou="company"
        )

        self.invoice = Invoice.objects.create(
            series="A",
            number="001",
            invoice_type="1.1",
            counterpart=self.client,
            counterpart_vat=self.client.afm,
            counterpart_name=self.client.eponimia,
            is_outgoing=True
        )

        self.product = Product.objects.create(
            code="PROD001",
            name="Test Product",
            unit="piece",
            sale_price=Decimal('100.00'),
            vat_category=1
        )

    def test_create_invoice_item(self):
        """Test creating an invoice item"""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            line_number=1,
            product=self.product,
            description="Test Product",
            quantity=Decimal('5.000'),
            unit="piece",
            unit_price=Decimal('20.00'),
            vat_category=1  # 24%
        )

        # Values should be auto-calculated
        self.assertEqual(item.net_value, Decimal('100.00'))
        self.assertEqual(item.vat_amount, Decimal('24.00'))

    def test_invoice_item_auto_calculations(self):
        """Test automatic value calculations"""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            line_number=1,
            description="Product",
            quantity=Decimal('3.000'),
            unit="piece",
            unit_price=Decimal('50.00'),
            vat_category=2  # 13%
        )

        # Net: 3 * 50 = 150
        # VAT: 150 * 0.13 = 19.50
        self.assertEqual(item.net_value, Decimal('150.00'))
        self.assertEqual(item.vat_amount, Decimal('19.50'))

    def test_invoice_item_zero_vat(self):
        """Test invoice item with zero VAT"""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            line_number=1,
            description="Product",
            quantity=Decimal('2.000'),
            unit="piece",
            unit_price=Decimal('100.00'),
            vat_category=7  # 0%
        )

        self.assertEqual(item.net_value, Decimal('200.00'))
        self.assertEqual(item.vat_amount, Decimal('0.00'))

    def test_invoice_item_updates_invoice_totals(self):
        """Test that adding items updates invoice totals"""
        InvoiceItem.objects.create(
            invoice=self.invoice,
            line_number=1,
            description="Item 1",
            quantity=Decimal('1.000'),
            unit="piece",
            unit_price=Decimal('100.00'),
            vat_category=1  # 24%
        )

        # Invoice should be updated
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.total_net, Decimal('100.00'))
        self.assertEqual(self.invoice.total_vat, Decimal('24.00'))


class MyDataSyncLogModelTest(TestCase):
    """Test MyDataSyncLog model"""

    def test_create_sync_log_success(self):
        """Test creating a successful sync log"""
        log = MyDataSyncLog.objects.create(
            sync_type='PULL_TRANSMITTED',
            status='SUCCESS',
            records_processed=50,
            records_created=10,
            records_updated=5,
            records_failed=0
        )

        self.assertEqual(log.sync_type, 'PULL_TRANSMITTED')
        self.assertEqual(log.status, 'SUCCESS')
        self.assertEqual(log.records_processed, 50)
        self.assertIsNotNone(log.started_at)

    def test_create_sync_log_error(self):
        """Test creating a failed sync log"""
        log = MyDataSyncLog.objects.create(
            sync_type='PUSH_INVOICE',
            status='ERROR',
            error_message="Connection timeout",
            records_failed=5
        )

        self.assertEqual(log.status, 'ERROR')
        self.assertEqual(log.error_message, "Connection timeout")
        self.assertEqual(log.records_failed, 5)

    def test_sync_log_with_details(self):
        """Test sync log with JSON details"""
        log = MyDataSyncLog.objects.create(
            sync_type='PULL_RECEIVED',
            status='SUCCESS',
            records_created=3,
            details={
                'invoices': ['A/001', 'A/002', 'A/003'],
                'date_range': '2024-03-01 to 2024-03-31'
            }
        )

        self.assertIsNotNone(log.details)
        self.assertEqual(len(log.details['invoices']), 3)
        self.assertIn('A/001', log.details['invoices'])

    def test_sync_log_completion_timestamp(self):
        """Test completion timestamp"""
        log = MyDataSyncLog.objects.create(
            sync_type='PUSH_INVOICE',
            status='PENDING'
        )

        self.assertIsNone(log.completed_at)

        # Mark as completed
        log.status = 'SUCCESS'
        log.completed_at = timezone.now()
        log.save()

        self.assertIsNotNone(log.completed_at)


class StockMovementIntegrationTest(TestCase):
    """Integration tests for stock movements with invoices"""

    def setUp(self):
        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Client",
            eidos_ipoxreou="company"
        )

        self.product = Product.objects.create(
            code="PROD001",
            name="Test Product",
            unit="piece",
            current_stock=Decimal('100.000'),
            purchase_price=Decimal('10.00'),
            sale_price=Decimal('20.00'),
            vat_category=1
        )

    def test_stock_movement_linked_to_invoice(self):
        """Test linking stock movement to invoice"""
        # Create invoice
        invoice = Invoice.objects.create(
            series="A",
            number="001",
            invoice_type="1.1",
            counterpart=self.client,
            counterpart_vat=self.client.afm,
            counterpart_name=self.client.eponimia,
            is_outgoing=True
        )

        # Add invoice item
        InvoiceItem.objects.create(
            invoice=invoice,
            line_number=1,
            product=self.product,
            description=self.product.name,
            quantity=Decimal('5.000'),
            unit=self.product.unit,
            unit_price=self.product.sale_price,
            vat_category=self.product.vat_category
        )

        # Create stock movement linked to invoice
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='OUT',
            quantity=Decimal('5.000'),
            invoice=invoice,
            counterpart=self.client
        )

        # Check link
        self.assertEqual(movement.invoice, invoice)
        self.assertIn(movement, invoice.stock_movements.all())

        # Stock should decrease
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, Decimal('95.000'))
