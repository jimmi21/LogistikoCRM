"""
Tests for Accounting email service
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import mail
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from accounting.models import (
    ClientProfile, ObligationType, MonthlyObligation,
    EmailTemplate, EmailAutomationRule, ScheduledEmail
)
from accounting.services.email_service import (
    create_scheduled_email, send_scheduled_email, trigger_automation_rules
)


class EmailServiceTest(TestCase):
    """Test email service functions"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Client Ltd",
            email="client@example.com",
            eidos_ipoxreou="company"
        )

        self.obl_type = ObligationType.objects.create(
            name="ΦΠΑ Μηνιαία",
            code="VAT_MONTHLY",
            frequency="monthly",
            deadline_type="last_day"
        )

        self.monthly_obl = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=self.obl_type,
            year=2024,
            month=3,
            deadline=datetime(2024, 3, 31).date(),
            status='pending'
        )

        self.template = EmailTemplate.objects.create(
            name="Completion Email",
            subject="Ολοκληρώθηκε: {{obligations.0.name}}",
            body_html="<p>Αγαπητέ {{client.eponimia}},</p><p>Η υποχρέωση ολοκληρώθηκε.</p>",
            is_active=True
        )

    def test_create_scheduled_email(self):
        """Test creating a scheduled email"""
        send_at = timezone.now() + timedelta(hours=1)

        scheduled_email = create_scheduled_email(
            obligations=[self.monthly_obl],
            template=self.template,
            recipient_email="test@example.com",
            send_at=send_at,
            user=self.user
        )

        self.assertIsNotNone(scheduled_email)
        self.assertEqual(scheduled_email.recipient_email, "test@example.com")
        self.assertEqual(scheduled_email.client, self.client)
        self.assertEqual(scheduled_email.template, self.template)
        self.assertEqual(scheduled_email.status, 'pending')
        self.assertIn('Test Client', scheduled_email.subject)

    def test_create_scheduled_email_uses_client_email_by_default(self):
        """Test that client email is used if recipient not specified"""
        scheduled_email = create_scheduled_email(
            obligations=[self.monthly_obl],
            template=self.template,
            user=self.user
        )

        self.assertEqual(
            scheduled_email.recipient_email,
            self.client.email
        )

    def test_create_scheduled_email_renders_template(self):
        """Test that template is rendered with proper context"""
        scheduled_email = create_scheduled_email(
            obligations=[self.monthly_obl],
            template=self.template,
            user=self.user
        )

        # Check rendered content
        self.assertIn('Test Client', scheduled_email.body_html)
        self.assertIn('ΦΠΑ Μηνιαία', scheduled_email.subject)

    def test_create_scheduled_email_with_multiple_obligations(self):
        """Test creating email with multiple obligations"""
        obl2 = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=ObligationType.objects.create(
                name="ΜΥΦ",
                code="MYF",
                frequency="monthly",
                deadline_type="specific_day",
                deadline_day=20
            ),
            year=2024,
            month=3,
            deadline=datetime(2024, 3, 20).date()
        )

        scheduled_email = create_scheduled_email(
            obligations=[self.monthly_obl, obl2],
            template=self.template,
            user=self.user
        )

        # Should have both obligations attached
        self.assertEqual(scheduled_email.obligations.count(), 2)

    def test_create_scheduled_email_with_empty_obligations(self):
        """Test that None is returned for empty obligations"""
        result = create_scheduled_email(
            obligations=[],
            template=self.template,
            user=self.user
        )

        self.assertIsNone(result)

    @patch('accounting.services.email_service.EmailMessage')
    def test_send_scheduled_email(self, mock_email_class):
        """Test sending a scheduled email"""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        # Create scheduled email
        scheduled_email = ScheduledEmail.objects.create(
            recipient_email="test@example.com",
            recipient_name="Test Recipient",
            client=self.client,
            template=self.template,
            subject="Test Subject",
            body_html="<p>Test Body</p>",
            send_at=timezone.now(),
            status='pending'
        )
        scheduled_email.obligations.add(self.monthly_obl)

        # Send
        result = send_scheduled_email(scheduled_email.id)

        # Check result
        self.assertTrue(result)

        # Check email was sent
        mock_email.send.assert_called_once()

        # Check scheduled email was marked as sent
        scheduled_email.refresh_from_db()
        self.assertEqual(scheduled_email.status, 'sent')
        self.assertIsNotNone(scheduled_email.sent_at)

    def test_send_scheduled_email_not_found(self):
        """Test sending non-existent email returns False"""
        result = send_scheduled_email(99999)
        self.assertFalse(result)

    def test_send_scheduled_email_already_sent(self):
        """Test that already sent emails are not re-sent"""
        scheduled_email = ScheduledEmail.objects.create(
            recipient_email="test@example.com",
            recipient_name="Test",
            client=self.client,
            template=self.template,
            subject="Test",
            body_html="<p>Test</p>",
            send_at=timezone.now(),
            status='sent'  # Already sent
        )

        result = send_scheduled_email(scheduled_email.id)
        self.assertFalse(result)

    @patch('accounting.services.email_service.EmailMessage')
    def test_send_scheduled_email_marks_failed_on_error(self, mock_email_class):
        """Test that failed emails are marked as failed"""
        mock_email = MagicMock()
        mock_email.send.side_effect = Exception("SMTP Error")
        mock_email_class.return_value = mock_email

        scheduled_email = ScheduledEmail.objects.create(
            recipient_email="test@example.com",
            recipient_name="Test",
            client=self.client,
            template=self.template,
            subject="Test",
            body_html="<p>Test</p>",
            send_at=timezone.now(),
            status='pending'
        )

        result = send_scheduled_email(scheduled_email.id)

        self.assertFalse(result)

        scheduled_email.refresh_from_db()
        self.assertEqual(scheduled_email.status, 'failed')
        self.assertIn('SMTP Error', scheduled_email.error_message)


class EmailAutomationRulesTest(TestCase):
    """Test email automation rules"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Client",
            email="client@example.com",
            eidos_ipoxreou="company"
        )

        self.obl_type = ObligationType.objects.create(
            name="ΦΠΑ Μηνιαία",
            code="VAT_MONTHLY",
            frequency="monthly",
            deadline_type="last_day"
        )

        self.monthly_obl = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=self.obl_type,
            year=2024,
            month=3,
            deadline=datetime(2024, 3, 31).date(),
            status='pending'
        )

        self.template = EmailTemplate.objects.create(
            name="Auto Email",
            subject="Αυτόματο email",
            body_html="<p>Test</p>",
            is_active=True
        )

    def test_trigger_automation_rule_on_complete(self):
        """Test triggering automation rule on completion"""
        rule = EmailAutomationRule.objects.create(
            name="Send on completion",
            trigger="on_complete",
            template=self.template,
            timing="immediate",
            is_active=True
        )

        # Trigger
        created_emails = trigger_automation_rules(
            self.monthly_obl,
            trigger_type='on_complete'
        )

        # Should create one email
        self.assertEqual(len(created_emails), 1)

        scheduled_email = created_emails[0]
        self.assertEqual(scheduled_email.automation_rule, rule)
        self.assertEqual(scheduled_email.client, self.client)

    def test_trigger_automation_rule_filtered_by_type(self):
        """Test that rules filter by obligation type"""
        # Create rule that only applies to different type
        other_type = ObligationType.objects.create(
            name="Other",
            code="OTHER",
            frequency="monthly",
            deadline_type="last_day"
        )

        rule = EmailAutomationRule.objects.create(
            name="Filtered rule",
            trigger="on_complete",
            template=self.template,
            timing="immediate",
            is_active=True
        )
        rule.filter_obligation_types.add(other_type)

        # Trigger - should not match
        created_emails = trigger_automation_rules(
            self.monthly_obl,
            trigger_type='on_complete'
        )

        # No emails should be created
        self.assertEqual(len(created_emails), 0)

    def test_trigger_automation_rule_timing_delay_1h(self):
        """Test delayed email scheduling"""
        rule = EmailAutomationRule.objects.create(
            name="Delayed email",
            trigger="on_complete",
            template=self.template,
            timing="delay_1h",
            is_active=True
        )

        created_emails = trigger_automation_rules(
            self.monthly_obl,
            trigger_type='on_complete'
        )

        scheduled_email = created_emails[0]

        # Should be scheduled ~1 hour from now
        time_diff = scheduled_email.send_at - timezone.now()
        self.assertGreater(time_diff.total_seconds(), 3500)  # ~58 minutes
        self.assertLess(time_diff.total_seconds(), 3700)  # ~62 minutes

    def test_trigger_automation_rule_inactive_skipped(self):
        """Test that inactive rules are not triggered"""
        rule = EmailAutomationRule.objects.create(
            name="Inactive rule",
            trigger="on_complete",
            template=self.template,
            timing="immediate",
            is_active=False  # Inactive
        )

        created_emails = trigger_automation_rules(
            self.monthly_obl,
            trigger_type='on_complete'
        )

        # No emails created
        self.assertEqual(len(created_emails), 0)

    def test_automation_rule_matches_obligation(self):
        """Test the matches_obligation method"""
        rule = EmailAutomationRule.objects.create(
            name="Test rule",
            trigger="on_complete",
            template=self.template,
            is_active=True
        )

        # Without filter - should match any
        self.assertTrue(rule.matches_obligation(self.monthly_obl))

        # With specific type filter
        rule.filter_obligation_types.add(self.obl_type)
        self.assertTrue(rule.matches_obligation(self.monthly_obl))

        # With different type filter
        other_type = ObligationType.objects.create(
            name="Other",
            code="OTHER",
            frequency="monthly",
            deadline_type="last_day"
        )
        rule.filter_obligation_types.clear()
        rule.filter_obligation_types.add(other_type)
        self.assertFalse(rule.matches_obligation(self.monthly_obl))

        # Inactive rule
        rule.is_active = False
        rule.save()
        self.assertFalse(rule.matches_obligation(self.monthly_obl))


class ScheduledEmailModelTest(TestCase):
    """Test ScheduledEmail model methods"""

    def setUp(self):
        self.client = ClientProfile.objects.create(
            afm="123456789",
            eponimia="Test Client",
            email="client@example.com",
            eidos_ipoxreou="company"
        )

        self.template = EmailTemplate.objects.create(
            name="Test Template",
            subject="Test",
            body_html="<p>Test</p>"
        )

    def test_get_attachments_from_obligations(self):
        """Test getting attachments from obligations"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        obl1 = MonthlyObligation.objects.create(
            client=self.client,
            obligation_type=ObligationType.objects.create(
                name="Type 1",
                code="T1",
                frequency="monthly",
                deadline_type="last_day"
            ),
            year=2024,
            month=3,
            deadline=datetime(2024, 3, 31).date()
        )

        # Add attachment
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        obl1.attachment = test_file
        obl1.save()

        scheduled_email = ScheduledEmail.objects.create(
            recipient_email="test@example.com",
            recipient_name="Test",
            client=self.client,
            template=self.template,
            subject="Test",
            body_html="<p>Test</p>",
            send_at=timezone.now()
        )
        scheduled_email.obligations.add(obl1)

        attachments = scheduled_email.get_attachments()

        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0], obl1.attachment)

    def test_mark_as_sent(self):
        """Test marking email as sent"""
        scheduled_email = ScheduledEmail.objects.create(
            recipient_email="test@example.com",
            recipient_name="Test",
            client=self.client,
            template=self.template,
            subject="Test",
            body_html="<p>Test</p>",
            send_at=timezone.now(),
            status='pending'
        )

        scheduled_email.mark_as_sent()

        self.assertEqual(scheduled_email.status, 'sent')
        self.assertIsNotNone(scheduled_email.sent_at)

    def test_mark_as_failed(self):
        """Test marking email as failed"""
        scheduled_email = ScheduledEmail.objects.create(
            recipient_email="test@example.com",
            recipient_name="Test",
            client=self.client,
            template=self.template,
            subject="Test",
            body_html="<p>Test</p>",
            send_at=timezone.now(),
            status='pending'
        )

        error_msg = "SMTP connection failed"
        scheduled_email.mark_as_failed(error_msg)

        self.assertEqual(scheduled_email.status, 'failed')
        self.assertEqual(scheduled_email.error_message, error_msg)
