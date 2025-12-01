"""
Tests for the Email Service
Author: ddiplas
Description: Tests for EmailTemplate, EmailLog, and EmailService functionality
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from decimal import Decimal

from accounting.models import (
    ClientProfile,
    ObligationType,
    MonthlyObligation,
    EmailTemplate,
    EmailLog
)
from accounting.services.email_service import EmailService

User = get_user_model()


class EmailTemplateModelTest(TestCase):
    """Tests for the EmailTemplate model"""

    def setUp(self):
        """Set up test data"""
        self.template = EmailTemplate.objects.create(
            name='Test Template',
            description='Test description',
            subject='Hello {client_name}',
            body_html='<p>Dear {client_name}, your {obligation_type} is complete.</p>',
            is_active=True
        )

    def test_template_creation(self):
        """Test that template is created correctly"""
        self.assertEqual(self.template.name, 'Test Template')
        self.assertTrue(self.template.is_active)

    def test_template_str(self):
        """Test template string representation"""
        self.assertEqual(str(self.template), 'Test Template')

    def test_render_simple_basic(self):
        """Test simple variable replacement"""
        variables = {
            'client_name': 'ΤΕΣΤ ΠΕΛΑΤΗΣ ΑΕ',
            'obligation_type': 'ΦΠΑ'
        }
        subject, body = self.template.render_simple(variables)

        self.assertEqual(subject, 'Hello ΤΕΣΤ ΠΕΛΑΤΗΣ ΑΕ')
        self.assertIn('ΤΕΣΤ ΠΕΛΑΤΗΣ ΑΕ', body)
        self.assertIn('ΦΠΑ', body)

    def test_render_simple_missing_variables(self):
        """Test handling of missing variables"""
        variables = {
            'client_name': 'Test Client'
            # obligation_type is missing
        }
        subject, body = self.template.render_simple(variables)

        # Missing variables should be replaced with empty string
        self.assertNotIn('{obligation_type}', body)

    def test_render_simple_greek_characters(self):
        """Test with Greek characters"""
        variables = {
            'client_name': 'ΔΟΚΙΜΑΣΤΙΚΗ ΕΤΑΙΡΕΙΑ ΑΕ',
            'obligation_type': 'Φόρος Προστιθέμενης Αξίας'
        }
        subject, body = self.template.render_simple(variables)

        self.assertIn('ΔΟΚΙΜΑΣΤΙΚΗ ΕΤΑΙΡΕΙΑ ΑΕ', subject)
        self.assertIn('Φόρος Προστιθέμενης Αξίας', body)

    def test_get_available_variables(self):
        """Test that available variables list is returned"""
        variables = EmailTemplate.get_available_variables()
        self.assertIsInstance(variables, list)
        self.assertTrue(len(variables) > 0)
        # Check some expected variables
        variable_names = [v[0] for v in variables]
        self.assertIn('{client_name}', variable_names)
        self.assertIn('{obligation_type}', variable_names)


class EmailTemplateSelectionTest(TestCase):
    """Tests for automatic template selection"""

    def setUp(self):
        """Set up test data"""
        self.obligation_type = ObligationType.objects.create(
            name='ΦΠΑ',
            code='FPA',
            frequency='monthly'
        )

        self.client = ClientProfile.objects.create(
            afm='123456789',
            eponimia='Test Company',
            email='test@example.com'
        )

        self.obligation = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=self.obligation_type,
            year=2025,
            month=1,
            deadline=timezone.now().date(),
            status='completed'
        )

        # Template specific to obligation type
        self.specific_template = EmailTemplate.objects.create(
            name='ΦΠΑ Template',
            subject='ΦΠΑ {period_display}',
            body_html='<p>ΦΠΑ completed</p>',
            obligation_type=self.obligation_type,
            is_active=True
        )

        # General template
        self.general_template = EmailTemplate.objects.create(
            name='Ολοκλήρωση Υποχρέωσης',
            subject='Ολοκλήρωση {obligation_type}',
            body_html='<p>General completion</p>',
            is_active=True
        )

    def test_get_template_for_specific_type(self):
        """Test that specific template is selected for obligation type"""
        template = EmailTemplate.get_template_for_obligation(self.obligation)
        self.assertEqual(template, self.specific_template)

    def test_get_template_fallback(self):
        """Test fallback to general template"""
        # Remove specific template
        self.specific_template.delete()

        template = EmailTemplate.get_template_for_obligation(self.obligation)
        self.assertEqual(template, self.general_template)


class EmailLogModelTest(TestCase):
    """Tests for the EmailLog model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

        self.client = ClientProfile.objects.create(
            afm='123456789',
            eponimia='Test Company',
            email='client@example.com'
        )

    def test_email_log_creation(self):
        """Test creating an email log entry"""
        log = EmailLog.objects.create(
            recipient_email='client@example.com',
            recipient_name='Test Company',
            client=self.client,
            subject='Test Subject',
            body='Test Body',
            status='sent',
            sent_by=self.user
        )

        self.assertEqual(log.status, 'sent')
        self.assertEqual(log.recipient_email, 'client@example.com')

    def test_email_log_str(self):
        """Test email log string representation"""
        log = EmailLog.objects.create(
            recipient_email='client@example.com',
            recipient_name='Test Company',
            subject='Test Subject',
            body='Test Body',
            status='sent'
        )

        str_repr = str(log)
        self.assertIn('client@example.com', str_repr)

    def test_email_log_status_display(self):
        """Test status display property"""
        log = EmailLog.objects.create(
            recipient_email='client@example.com',
            recipient_name='Test Company',
            subject='Test Subject',
            body='Test Body',
            status='sent'
        )

        self.assertIn('Απεστάλη', log.status_display)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='noreply@test.com'
)
class EmailServiceTest(TestCase):
    """Tests for the EmailService class"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

        self.obligation_type = ObligationType.objects.create(
            name='ΦΠΑ',
            code='FPA',
            frequency='monthly'
        )

        self.client = ClientProfile.objects.create(
            afm='123456789',
            eponimia='ΤΕΣΤ ΕΤΑΙΡΕΙΑ ΑΕ',
            email='client@example.com'
        )

        self.obligation = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=self.obligation_type,
            year=2025,
            month=1,
            deadline=timezone.now().date(),
            status='completed'
        )

        self.template = EmailTemplate.objects.create(
            name='Ολοκλήρωση Υποχρέωσης',
            subject='Ολοκλήρωση {obligation_type} - {period_display}',
            body_html='<p>Αγαπητέ {client_name}, η υποχρέωση {obligation_type} ολοκληρώθηκε.</p>',
            is_active=True
        )

    def test_get_context_for_obligation(self):
        """Test context generation for obligation"""
        context = EmailService.get_context_for_obligation(self.obligation, self.user)

        self.assertEqual(context['client_name'], 'ΤΕΣΤ ΕΤΑΙΡΕΙΑ ΑΕ')
        self.assertEqual(context['client_afm'], '123456789')
        self.assertEqual(context['obligation_type'], 'ΦΠΑ')
        self.assertEqual(context['period_month'], '01')
        self.assertEqual(context['period_year'], '2025')

    def test_render_template(self):
        """Test template rendering"""
        subject, body = EmailService.render_template(
            template=self.template,
            obligation=self.obligation,
            user=self.user
        )

        self.assertIn('ΦΠΑ', subject)
        self.assertIn('01/2025', subject)
        self.assertIn('ΤΕΣΤ ΕΤΑΙΡΕΙΑ ΑΕ', body)

    def test_send_email(self):
        """Test sending email"""
        success, result = EmailService.send_email(
            recipient_email='test@example.com',
            subject='Test Subject',
            body='<p>Test Body</p>',
            client=self.client,
            template=self.template,
            user=self.user
        )

        self.assertTrue(success)
        self.assertIsInstance(result, EmailLog)
        self.assertEqual(result.status, 'sent')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')

    def test_send_email_creates_log(self):
        """Test that sending email creates a log entry"""
        initial_count = EmailLog.objects.count()

        EmailService.send_email(
            recipient_email='test@example.com',
            subject='Test Subject',
            body='<p>Test Body</p>',
            client=self.client,
            user=self.user
        )

        self.assertEqual(EmailLog.objects.count(), initial_count + 1)

    def test_send_obligation_completion_email(self):
        """Test sending completion email for obligation"""
        success, result = EmailService.send_obligation_completion_email(
            obligation=self.obligation,
            user=self.user
        )

        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('ΦΠΑ', mail.outbox[0].subject)

    def test_send_obligation_completion_email_no_client_email(self):
        """Test handling when client has no email"""
        self.client.email = ''
        self.client.save()

        success, result = EmailService.send_obligation_completion_email(
            obligation=self.obligation,
            user=self.user
        )

        self.assertFalse(success)
        self.assertEqual(len(mail.outbox), 0)

    def test_preview_email(self):
        """Test email preview functionality"""
        preview = EmailService.preview_email(
            template=self.template,
            obligation=self.obligation,
            user=self.user
        )

        self.assertIn('subject', preview)
        self.assertIn('body', preview)
        self.assertIn('recipient', preview)
        self.assertEqual(preview['recipient'], 'client@example.com')
        self.assertIn('ΦΠΑ', preview['subject'])

    def test_send_bulk_emails(self):
        """Test sending bulk emails"""
        # Create another obligation
        obligation2 = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=self.obligation_type,
            year=2025,
            month=2,
            deadline=timezone.now().date(),
            status='completed'
        )

        results = EmailService.send_bulk_emails(
            obligations=[self.obligation, obligation2],
            template=self.template,
            user=self.user
        )

        self.assertEqual(results['sent'], 2)
        self.assertEqual(results['failed'], 0)
        self.assertEqual(len(mail.outbox), 2)


class EmailServiceGreekCharactersTest(TestCase):
    """Tests for Greek character handling in emails"""

    def setUp(self):
        """Set up test data with Greek characters"""
        self.obligation_type = ObligationType.objects.create(
            name='Φόρος Προστιθέμενης Αξίας',
            code='ΦΠΑ',
            frequency='monthly'
        )

        self.client = ClientProfile.objects.create(
            afm='123456789',
            eponimia='ΔΟΚΙΜΑΣΤΙΚΗ ΕΤΑΙΡΕΙΑ ΜΟΝΟΠΡΟΣΩΠΗ ΙΚΕ',
            email='info@dokimastiki.gr'
        )

        self.template = EmailTemplate.objects.create(
            name='Ελληνικό Template',
            subject='Ολοκλήρωση {obligation_type} για {client_name}',
            body_html='''
                <p>Αγαπητοί κύριοι,</p>
                <p>Σας ενημερώνουμε ότι η υποχρέωση {obligation_type}
                για την περίοδο {period_display} ολοκληρώθηκε.</p>
                <p>Με εκτίμηση,<br>{accountant_name}</p>
            ''',
            is_active=True
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@test.com',
        ACCOUNTANT_NAME='Ιωάννης Παπαδόπουλος'
    )
    def test_greek_characters_in_email(self):
        """Test that Greek characters are preserved in emails"""
        obligation = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=self.obligation_type,
            year=2025,
            month=3,
            deadline=timezone.now().date(),
            status='completed'
        )

        success, result = EmailService.send_obligation_completion_email(
            obligation=obligation
        )

        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)

        # Check subject contains Greek
        self.assertIn('Φόρος Προστιθέμενης Αξίας', mail.outbox[0].subject)
        self.assertIn('ΔΟΚΙΜΑΣΤΙΚΗ', mail.outbox[0].subject)
