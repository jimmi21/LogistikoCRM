"""
Email Service for LogistikoCRM
Author: ddiplas
Version: 2.0
Description: Complete email service with direct SMTP sending and logging.
             No Celery required - emails are sent synchronously.
"""

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for sending templated emails from the CRM.

    Features:
    - Direct SMTP sending (no Celery)
    - Email logging with EmailLog model
    - Template rendering with {variable} syntax
    - Preview functionality
    - Attachment support
    """

    @staticmethod
    def get_context_for_obligation(obligation, user=None):
        """
        Build context dictionary for an obligation.

        Args:
            obligation: MonthlyObligation instance
            user: Optional User who is sending the email

        Returns:
            dict with all available template variables
        """
        client = obligation.client
        obl_type = obligation.obligation_type

        # Greek month names
        month_names = {
            1: 'Ιανουάριος', 2: 'Φεβρουάριος', 3: 'Μάρτιος',
            4: 'Απρίλιος', 5: 'Μάιος', 6: 'Ιούνιος',
            7: 'Ιούλιος', 8: 'Αύγουστος', 9: 'Σεπτέμβριος',
            10: 'Οκτώβριος', 11: 'Νοέμβριος', 12: 'Δεκέμβριος'
        }

        context = {
            # Client variables
            'client_name': client.eponimia,
            'client_afm': client.afm,
            'client_email': client.email or '',
            'client_phone': client.kinito_tilefono or client.tilefono_epixeirisis_1 or '',

            # Obligation variables
            'obligation_type': obl_type.name if obl_type else '',
            'obligation_code': obl_type.code if obl_type else '',
            'period_month': f"{obligation.month:02d}",
            'period_month_name': month_names.get(obligation.month, ''),
            'period_year': str(obligation.year),
            'period_display': f"{obligation.month:02d}/{obligation.year}",
            'deadline': obligation.deadline.strftime('%d/%m/%Y') if obligation.deadline else '',
            'completed_date': timezone.now().date().strftime('%d/%m/%Y'),

            # Company/Accountant variables (from settings)
            'accountant_name': getattr(settings, 'ACCOUNTANT_NAME', 'Λογιστικό Γραφείο'),
            'accountant_title': getattr(settings, 'ACCOUNTANT_TITLE', ''),
            'company_name': getattr(settings, 'COMPANY_NAME', 'Λογιστικό Γραφείο'),
            'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
            'company_website': getattr(settings, 'COMPANY_WEBSITE', ''),
            'email_signature': getattr(settings, 'EMAIL_SIGNATURE', ''),

            # User who sent the email
            'sender_name': user.get_full_name() if user else getattr(settings, 'ACCOUNTANT_NAME', ''),
        }

        return context

    @staticmethod
    def render_template(template, obligation=None, client=None, extra_context=None, user=None):
        """
        Render an email template with the given context.

        Args:
            template: EmailTemplate instance
            obligation: Optional MonthlyObligation instance
            client: Optional ClientProfile instance (used if no obligation)
            extra_context: Optional dict with additional context variables
            user: Optional User who is sending

        Returns:
            tuple: (rendered_subject, rendered_body)
        """
        context = {}

        # Build context from obligation
        if obligation:
            context = EmailService.get_context_for_obligation(obligation, user)
        elif client:
            # Build minimal context from client
            context = {
                'client_name': client.eponimia,
                'client_afm': client.afm,
                'client_email': client.email or '',
                'accountant_name': getattr(settings, 'ACCOUNTANT_NAME', 'Λογιστικό Γραφείο'),
                'company_name': getattr(settings, 'COMPANY_NAME', 'Λογιστικό Γραφείο'),
                'completed_date': timezone.now().date().strftime('%d/%m/%Y'),
            }

        # Add any extra context
        if extra_context:
            context.update(extra_context)

        # Render using simple {variable} syntax
        return template.render_simple(context)

    @staticmethod
    def send_email(
        recipient_email,
        subject,
        body,
        client=None,
        obligation=None,
        template=None,
        user=None,
        attachments=None,
        html_body=None
    ):
        """
        Send an email and log it.

        Args:
            recipient_email: Email address to send to
            subject: Email subject
            body: Email body (HTML or plain text)
            client: Optional ClientProfile for logging
            obligation: Optional MonthlyObligation for logging
            template: Optional EmailTemplate used
            user: Optional User who is sending
            attachments: Optional list of file paths or (filename, content, mimetype) tuples
            html_body: Optional separate HTML body (if body is plain text)

        Returns:
            tuple: (success: bool, email_log: EmailLog or error_message: str)
        """
        from accounting.models import EmailLog

        # Create email log entry
        email_log = EmailLog.objects.create(
            recipient_email=recipient_email,
            recipient_name=client.eponimia if client else recipient_email,
            client=client,
            obligation=obligation,
            template_used=template,
            subject=subject,
            body=body,
            status='pending',
            sent_by=user
        )

        try:
            # Check email configuration
            if not getattr(settings, 'EMAIL_HOST', None):
                raise ValueError("EMAIL_HOST δεν έχει οριστεί στις ρυθμίσεις")

            # Check if using console backend (for testing)
            is_console_backend = getattr(settings, 'EMAIL_BACKEND', '').endswith('console.EmailBackend')

            if not is_console_backend:
                if not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
                    logger.warning("EMAIL_HOST_PASSWORD δεν έχει οριστεί - email ίσως αποτύχει")

            # Prepare email
            if html_body:
                # Send as multipart (plain + HTML)
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=strip_tags(body),  # Plain text version
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email]
                )
                email.attach_alternative(html_body, "text/html")
            else:
                # Send as HTML
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email]
                )
                email.content_subtype = 'html'

            # Add attachments
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, str):
                        # File path
                        email.attach_file(attachment)
                    elif isinstance(attachment, tuple) and len(attachment) == 3:
                        # (filename, content, mimetype)
                        email.attach(*attachment)
                    elif hasattr(attachment, 'path'):
                        # Django FileField
                        try:
                            email.attach_file(attachment.path)
                        except Exception as e:
                            logger.warning(f"Could not attach file {attachment}: {e}")

            # Send email
            email.send(fail_silently=False)

            # Update log as sent
            email_log.status = 'sent'
            email_log.save()

            logger.info(f"✅ Email sent to {recipient_email}: {subject}")
            return True, email_log

        except Exception as e:
            # Update log as failed
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save()

            logger.error(f"❌ Failed to send email to {recipient_email}: {e}")
            return False, str(e)

    @staticmethod
    def send_obligation_completion_email(obligation, user=None, include_attachment=True):
        """
        Send completion notification for an obligation.

        Args:
            obligation: MonthlyObligation instance
            user: Optional User who completed the obligation
            include_attachment: Whether to include the obligation attachment

        Returns:
            tuple: (success: bool, email_log or error_message)
        """
        from accounting.models import EmailTemplate

        client = obligation.client

        # Check if client has email
        if not client.email:
            logger.warning(f"Cannot send email for {obligation}: client has no email")
            return False, "Ο πελάτης δεν έχει email"

        # Get appropriate template
        template = EmailTemplate.get_template_for_obligation(obligation)

        if not template:
            logger.warning(f"No email template found for {obligation}")
            return False, "Δεν βρέθηκε πρότυπο email"

        # Render template
        subject, body = EmailService.render_template(
            template=template,
            obligation=obligation,
            user=user
        )

        # Prepare attachments
        attachments = []
        if include_attachment and obligation.attachment:
            try:
                attachments.append(obligation.attachment)
            except Exception as e:
                logger.warning(f"Could not add attachment: {e}")

        # Send email
        return EmailService.send_email(
            recipient_email=client.email,
            subject=subject,
            body=body,
            client=client,
            obligation=obligation,
            template=template,
            user=user,
            attachments=attachments
        )

    @staticmethod
    def preview_email(template, obligation=None, client=None, extra_context=None, user=None):
        """
        Preview email without sending.

        Returns:
            dict with 'subject', 'body', and 'recipient'
        """
        subject, body = EmailService.render_template(
            template=template,
            obligation=obligation,
            client=client,
            extra_context=extra_context,
            user=user
        )

        recipient = ''
        if obligation and obligation.client:
            recipient = obligation.client.email or ''
        elif client:
            recipient = client.email or ''

        return {
            'subject': subject,
            'body': body,
            'recipient': recipient,
            'recipient_name': client.eponimia if client else (obligation.client.eponimia if obligation else ''),
        }

    @staticmethod
    def send_bulk_emails(obligations, template=None, user=None, include_attachments=True):
        """
        Send emails for multiple obligations.

        Args:
            obligations: QuerySet or list of MonthlyObligation instances
            template: Optional specific template (otherwise auto-selects)
            user: User who is sending
            include_attachments: Whether to include obligation attachments

        Returns:
            dict with 'sent', 'failed', 'skipped' counts and 'details' list
        """
        results = {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        for obligation in obligations:
            client = obligation.client

            # Skip if no email
            if not client.email:
                results['skipped'] += 1
                results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'skipped',
                    'message': 'Δεν υπάρχει email'
                })
                continue

            # Use specific template or find appropriate one
            email_template = template
            if not email_template:
                from accounting.models import EmailTemplate
                email_template = EmailTemplate.get_template_for_obligation(obligation)

            if not email_template:
                results['failed'] += 1
                results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'failed',
                    'message': 'Δεν βρέθηκε πρότυπο'
                })
                continue

            # Send email
            success, result = EmailService.send_obligation_completion_email(
                obligation=obligation,
                user=user,
                include_attachment=include_attachments
            )

            if success:
                results['sent'] += 1
                results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'sent',
                    'message': f'Στάλθηκε στο {client.email}'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'failed',
                    'message': str(result)
                })

        logger.info(f"Bulk email results: sent={results['sent']}, failed={results['failed']}, skipped={results['skipped']}")
        return results


# ============================================================================
# LEGACY FUNCTIONS (for backwards compatibility with existing code)
# ============================================================================

def create_scheduled_email(obligations, template, recipient_email=None, send_at=None, user=None):
    """
    Create a scheduled email for obligations.
    LEGACY: This function maintains backwards compatibility.
    For new code, use EmailService.send_email directly.
    """
    from accounting.models import ScheduledEmail
    from django.conf import settings

    if not obligations:
        return None

    obligations_list = list(obligations)
    client = obligations_list[0].client

    # Build context
    context = EmailService.get_context_for_obligation(obligations_list[0], user)

    # Add obligations list for multi-obligation emails
    context['obligations'] = [
        {
            'name': obl.obligation_type.name,
            'deadline': obl.deadline.strftime('%d/%m/%Y'),
            'status': obl.get_status_display(),
        }
        for obl in obligations_list
    ]

    # Render template using legacy method
    subject, body = template.render({
        'client': {
            'eponimia': client.eponimia,
            'afm': client.afm,
            'email': client.email,
        },
        'obligations': context['obligations'],
        'user': {
            'name': user.get_full_name() if user else context['accountant_name'],
        },
        **context
    })

    # Create scheduled email
    scheduled_email = ScheduledEmail.objects.create(
        recipient_email=recipient_email or client.email,
        recipient_name=client.eponimia,
        client=client,
        template=template,
        subject=subject,
        body_html=body,
        send_at=send_at or timezone.now(),
        created_by=user,
    )

    scheduled_email.obligations.set(obligations_list)

    return scheduled_email


def send_scheduled_email(email_id):
    """
    Send a scheduled email.
    LEGACY: Maintains backwards compatibility.
    """
    from accounting.models import ScheduledEmail

    try:
        scheduled_email = ScheduledEmail.objects.get(pk=email_id, status='pending')
    except ScheduledEmail.DoesNotExist:
        logger.error(f"ScheduledEmail {email_id} not found or not pending")
        return False

    try:
        email = EmailMessage(
            subject=scheduled_email.subject,
            body=scheduled_email.body_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[scheduled_email.recipient_email],
        )
        email.content_subtype = 'html'

        # Attach files
        attachments = scheduled_email.get_attachments()
        for attachment in attachments:
            try:
                email.attach_file(attachment.path)
            except Exception as e:
                logger.warning(f"Could not attach file: {e}")

        email.send()
        scheduled_email.mark_as_sent()

        logger.info(f"✅ Scheduled email sent to {scheduled_email.recipient_email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send scheduled email {email_id}: {str(e)}")
        scheduled_email.mark_as_failed(str(e))
        return False


def trigger_automation_rules(obligation, trigger_type='on_complete'):
    """
    Trigger automation rules for an obligation.
    LEGACY: For new code, use EmailService.send_obligation_completion_email directly.
    """
    from accounting.models import EmailAutomationRule

    rules = EmailAutomationRule.objects.filter(
        is_active=True,
        trigger=trigger_type
    )

    created_emails = []

    for rule in rules:
        if not rule.matches_obligation(obligation):
            continue

        # For immediate sending, use new EmailService
        if rule.timing == 'immediate':
            success, result = EmailService.send_obligation_completion_email(
                obligation=obligation,
                user=None
            )
            if success:
                logger.info(f"📧 Email sent via rule '{rule.name}' for {obligation}")
        else:
            # For delayed/scheduled, create scheduled email
            if rule.timing == 'delay_1h':
                send_at = timezone.now() + timezone.timedelta(hours=1)
            elif rule.timing == 'delay_24h':
                send_at = timezone.now() + timezone.timedelta(days=1)
            elif rule.timing == 'scheduled' and rule.scheduled_time:
                send_at = timezone.now().replace(
                    hour=rule.scheduled_time.hour,
                    minute=rule.scheduled_time.minute,
                    second=0
                )
                if send_at < timezone.now():
                    send_at += timezone.timedelta(days=1)
            else:
                send_at = timezone.now()

            scheduled_email = create_scheduled_email(
                obligations=[obligation],
                template=rule.template,
                send_at=send_at,
                user=None
            )

            if scheduled_email:
                scheduled_email.automation_rule = rule
                scheduled_email.save()
                created_emails.append(scheduled_email)
                logger.info(f"📧 Scheduled email via rule '{rule.name}' for {obligation}")

    return created_emails
