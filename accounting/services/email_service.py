from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from accounting.models import ScheduledEmail, EmailTemplate, EmailAutomationRule
import logging

logger = logging.getLogger(__name__)


def create_scheduled_email(obligations, template, recipient_email=None, send_at=None, user=None):
    """
    Create a scheduled email for obligations with personalized context
    """
    from django.conf import settings
    
    if not obligations:
        return None
    
    obligations_list = list(obligations)
    client = obligations_list[0].client
    
    # PERSONALIZED CONTEXT από settings!
    context = {
        'client': {
            'eponimia': client.eponimia,
            'afm': client.afm,
            'email': client.email,
        },
        'obligations': [
            {
                'name': obl.obligation_type.name,
                'deadline': obl.deadline.strftime('%d/%m/%Y'),
                'status': obl.get_status_display(),
            }
            for obl in obligations_list
        ],
        'user': {
            'name': user.get_full_name() if user else settings.ACCOUNTANT_NAME,
        },
        # PERSONALIZED από settings!
        'company_name': settings.COMPANY_NAME,
        'company_short_name': settings.COMPANY_SHORT_NAME,
        'accountant_name': settings.ACCOUNTANT_NAME,
        'accountant_title': settings.ACCOUNTANT_TITLE,
        'email_signature': settings.EMAIL_SIGNATURE,
        'website': settings.COMPANY_WEBSITE,
        'phone': settings.COMPANY_PHONE,
        'completed_date': timezone.now().date().strftime('%d/%m/%Y'),
    }
    
    # Render template
    subject, body = template.render(context)
    
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
    """Send a scheduled email"""
    try:
        scheduled_email = ScheduledEmail.objects.get(pk=email_id, status='pending')
    except ScheduledEmail.DoesNotExist:
        logger.error(f"ScheduledEmail {email_id} not found or not pending")
        return False
    
    try:
        # Create email message
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
            email.attach_file(attachment.path)
        
        # Send
        email.send()
        
        # Mark as sent
        scheduled_email.mark_as_sent()
        
        logger.info(f"✅ Email sent to {scheduled_email.recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email {email_id}: {str(e)}")
        scheduled_email.mark_as_failed(str(e))
        return False


def trigger_automation_rules(obligation, trigger_type='on_complete'):
    """
    Trigger automation rules for an obligation
    
    Args:
        obligation: MonthlyObligation instance
        trigger_type: 'on_complete', 'before_deadline', 'on_overdue'
    """
    rules = EmailAutomationRule.objects.filter(
        is_active=True,
        trigger=trigger_type
    )
    
    created_emails = []
    
    for rule in rules:
        if not rule.matches_obligation(obligation):
            continue
        
        # Calculate send time based on timing
        if rule.timing == 'immediate':
            send_at = timezone.now()
        elif rule.timing == 'delay_1h':
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
        
        # Create scheduled email
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
            
            logger.info(f"📧 Created scheduled email via rule '{rule.name}' for {obligation}")
    
    return created_emails