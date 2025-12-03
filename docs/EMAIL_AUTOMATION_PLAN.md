# Email Automation Analysis & Implementation Plan

**Project:** LogistikoCRM
**Analysis Date:** December 2025
**Author:** Claude Analysis
**Status:** Post-VoIP Phase 1, Pre-Email Automation Implementation

---

## 1. Current State Analysis

### 1.1 Existing Components

#### Models (accounting/models.py)

| Model | Status | Description |
|-------|--------|-------------|
| `EmailTemplate` | **Complete** | Full template system with `{variable}` syntax, auto-selection by obligation type |
| `EmailLog` | **Complete** | Tracks all sent emails, status (sent/failed/pending), indexing |
| `EmailAutomationRule` | **Complete** | Triggers: on_complete, before_deadline, on_overdue, manual |
| `ScheduledEmail` | **Complete** | Queue for delayed emails, ManyToMany with obligations |

**Template Variables Supported:**
- `{client_name}`, `{client_afm}`, `{client_email}`
- `{obligation_type}`, `{deadline}`, `{period_display}`
- `{accountant_name}`, `{company_name}`

#### Services (accounting/services/email_service.py)

| Feature | Status | Notes |
|---------|--------|-------|
| `EmailService.send_email()` | **Complete** | Direct SMTP, logging, attachments |
| `EmailService.render_template()` | **Complete** | Context building, variable replacement |
| `EmailService.send_bulk_emails()` | **Complete** | Batch sending with progress tracking |
| `EmailService.preview_email()` | **Complete** | Preview without sending |
| `trigger_automation_rules()` | **Partial** | Creates scheduled emails but no processor |
| `send_scheduled_email()` | **Complete** | Sends single scheduled email |

#### Celery Tasks (accounting/tasks.py)

| Task | Status | Schedule |
|------|--------|----------|
| `send_obligation_reminders` | **Active** | 09:00 Mon-Fri |
| `send_daily_summary` | **Active** | 17:00 Mon-Fri |
| `process_pending_tickets` | **Active** | Hourly |
| `create_or_update_ticket_for_missed_call` | **Active** | On demand |

#### Configuration (webcrm/settings.py)

```python
# Email Backend - CONFIGURED
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Celery - CONFIGURED
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Beat Schedule - CONFIGURED
CELERY_BEAT_SCHEDULE = {
    'send-obligation-reminders': {...},  # 09:00 Mon-Fri
    'send-daily-summary': {...},         # 17:00 Mon-Fri
}
```

#### Tests (tests/accounting/test_email_service.py)

| Test Category | Coverage |
|---------------|----------|
| Template rendering | **Complete** |
| Template selection | **Complete** |
| Email sending | **Complete** |
| Greek characters | **Complete** |
| Bulk emails | **Complete** |

---

### 1.2 Gaps Identified

| Gap | Severity | Impact |
|-----|----------|--------|
| No `process_scheduled_emails` task | **HIGH** | ScheduledEmail records never sent |
| No overdue notifications to clients | **MEDIUM** | Clients don't know about missed deadlines |
| No document upload confirmation | **LOW** | Nice-to-have feature |
| No Celery beat for before_deadline rules | **HIGH** | Automation rules don't trigger |
| Massmail not integrated | **LOW** | Separate system exists |

---

## 2. Requirements Analysis

### 2.1 Accounting Office Needs

#### A. Monthly Obligation Reminders
- **Current State:** Partially implemented
- **What Works:** `send_obligation_reminders` task sends emails for obligations due in 7 days
- **Gap:** Only sends to clients, no configurable days before deadline

#### B. Overdue Notifications
- **Current State:** Not implemented for clients
- **What Works:** Daily summary includes overdue count for staff
- **Gap:** No email to clients about their overdue obligations

#### C. Document Upload Confirmations
- **Current State:** Not implemented
- **Gap:** No signal/trigger when files are uploaded

#### D. Bulk Email for Announcements
- **Current State:** Basic support via `send_bulk_emails()`
- **Gap:** No admin UI for mass announcements

---

## 3. Technical Assessment

### 3.1 Celery Status

**Verdict: Properly Configured**

```python
# webcrm/celery.py - Minimal but correct
app = Celery('webcrm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Recommendation:** Works correctly. Redis broker configured.

### 3.2 Email Backend Status

**Verdict: Production Ready**

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # Secure
EMAIL_USE_TLS = True
```

**Recommendation:** Gmail SMTP ready. Consider SendGrid for high volume.

### 3.3 Architecture Assessment

**Strengths:**
- Clean separation: Models -> Services -> Tasks
- Good test coverage
- Proper logging
- Greek character support verified

**Weaknesses:**
- ScheduledEmail queue never processed
- EmailAutomationRule.before_deadline not triggered
- No Django signal for document uploads

---

## 4. Implementation Priority

### Priority 1: Critical (Must Have)

| Task | Effort | Description |
|------|--------|-------------|
| `process_scheduled_emails` task | 2h | Celery task to process ScheduledEmail queue |
| `check_deadline_reminders` task | 3h | Trigger EmailAutomationRule.before_deadline |
| Add to Celery Beat schedule | 30m | Schedule new tasks |

### Priority 2: High (Should Have)

| Task | Effort | Description |
|------|--------|-------------|
| Overdue notification task | 2h | Email clients about overdue obligations |
| Admin action: Send Reminder | 1h | Manual trigger from admin |
| Email preview in admin | 2h | Preview before sending |

### Priority 3: Medium (Nice to Have)

| Task | Effort | Description |
|------|--------|-------------|
| Document upload confirmation | 3h | Signal + email on upload |
| Email template admin improvements | 2h | Variable help, preview |
| Unsubscribe mechanism | 4h | Per-client opt-out |

### Priority 4: Low (Future)

| Task | Effort | Description |
|------|--------|-------------|
| SendGrid integration | 4h | High-volume email service |
| Email analytics dashboard | 8h | Open rates, delivery stats |
| Massmail integration | 4h | Connect to existing massmail app |

---

## 5. Detailed Implementation Plan

### Phase 1: Fix Critical Gaps (Day 1)

#### Task 1.1: Create `process_scheduled_emails` Task

**File:** `accounting/tasks.py`

```python
@shared_task
def process_scheduled_emails():
    """
    Process pending scheduled emails.
    Runs: Every 5 minutes
    """
    from accounting.models import ScheduledEmail
    from accounting.services.email_service import send_scheduled_email

    now = timezone.now()
    pending = ScheduledEmail.objects.filter(
        status='pending',
        send_at__lte=now
    ).select_related('client', 'template')[:50]  # Batch limit

    sent = 0
    failed = 0

    for email in pending:
        success = send_scheduled_email(email.id)
        if success:
            sent += 1
        else:
            failed += 1

    return f"Processed: {sent} sent, {failed} failed"
```

#### Task 1.2: Create `check_deadline_reminders` Task

**File:** `accounting/tasks.py`

```python
@shared_task
def check_deadline_reminders():
    """
    Check for obligations approaching deadline and trigger reminders.
    Runs: Daily at 08:00
    """
    from accounting.models import EmailAutomationRule, MonthlyObligation

    today = timezone.now().date()

    # Get all active "before_deadline" rules
    rules = EmailAutomationRule.objects.filter(
        is_active=True,
        trigger='before_deadline',
        days_before_deadline__isnull=False
    )

    created = 0
    for rule in rules:
        target_date = today + timedelta(days=rule.days_before_deadline)

        obligations = MonthlyObligation.objects.filter(
            deadline=target_date,
            status='pending',
            client__email__isnull=False
        ).exclude(client__email='')

        # Filter by obligation types if specified
        if rule.filter_obligation_types.exists():
            obligations = obligations.filter(
                obligation_type__in=rule.filter_obligation_types.all()
            )

        for obl in obligations:
            # Check if already scheduled
            if not ScheduledEmail.objects.filter(
                client=obl.client,
                automation_rule=rule,
                obligations=obl,
                status='pending'
            ).exists():
                create_scheduled_email(
                    obligations=[obl],
                    template=rule.template,
                    send_at=timezone.now()
                )
                created += 1

    return f"Created {created} reminder emails"
```

#### Task 1.3: Update Celery Beat Schedule

**File:** `webcrm/settings.py`

```python
CELERY_BEAT_SCHEDULE = {
    'send-obligation-reminders': {
        'task': 'accounting.tasks.send_obligation_reminders',
        'schedule': crontab(hour=9, minute=0, day_of_week='1-5'),
    },
    'send-daily-summary': {
        'task': 'accounting.tasks.send_daily_summary',
        'schedule': crontab(hour=17, minute=0, day_of_week='1-5'),
    },
    # NEW TASKS
    'process-scheduled-emails': {
        'task': 'accounting.tasks.process_scheduled_emails',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-deadline-reminders': {
        'task': 'accounting.tasks.check_deadline_reminders',
        'schedule': crontab(hour=8, minute=0),  # Daily at 08:00
    },
}
```

---

### Phase 2: Overdue Notifications (Day 2)

#### Task 2.1: Create `send_overdue_notifications` Task

```python
@shared_task
def send_overdue_notifications():
    """
    Send notifications for overdue obligations.
    Runs: Daily at 10:00
    """
    from accounting.models import MonthlyObligation, EmailTemplate
    from accounting.services.email_service import EmailService

    today = timezone.now().date()

    # Get overdue obligations grouped by client
    overdue = MonthlyObligation.objects.filter(
        status__in=['pending', 'overdue'],
        deadline__lt=today,
        client__email__isnull=False
    ).exclude(client__email='').select_related('client', 'obligation_type')

    # Group by client
    clients = {}
    for obl in overdue:
        if obl.client_id not in clients:
            clients[obl.client_id] = {
                'client': obl.client,
                'obligations': []
            }
        clients[obl.client_id]['obligations'].append(obl)

    # Get overdue template
    template = EmailTemplate.objects.filter(
        is_active=True,
        name__icontains='overdue'
    ).first()

    if not template:
        logger.warning("No overdue template found")
        return "No template"

    sent = 0
    for data in clients.values():
        client = data['client']
        obls = data['obligations']

        # Build obligations list for template
        context = {
            'client_name': client.eponimia,
            'overdue_count': len(obls),
            'obligations_list': ', '.join([o.obligation_type.name for o in obls]),
        }

        subject, body = template.render_simple(context)

        success, _ = EmailService.send_email(
            recipient_email=client.email,
            subject=subject,
            body=body,
            client=client,
            template=template
        )

        if success:
            sent += 1

    return f"Sent {sent} overdue notifications"
```

---

### Phase 3: Admin Improvements (Day 3)

#### Task 3.1: Add Admin Actions

**File:** `accounting/admin.py`

```python
@admin.action(description="Send reminder email to selected")
def send_reminder_email(modeladmin, request, queryset):
    """Send reminder emails for selected obligations"""
    from accounting.services.email_service import EmailService

    results = EmailService.send_bulk_emails(
        obligations=queryset,
        user=request.user
    )

    modeladmin.message_user(
        request,
        f"Sent: {results['sent']}, Failed: {results['failed']}, Skipped: {results['skipped']}"
    )

class MonthlyObligationAdmin(admin.ModelAdmin):
    actions = [send_reminder_email, ...]
```

---

## 6. Email Templates Needed

### 6.1 Template: Obligation Completion (Exists)
```
Subject: Ολοκλήρωση {obligation_type} - {period_display}
```

### 6.2 Template: Deadline Reminder (Create)
```
Subject: Υπενθύμιση: {obligation_type} λήγει σε {days_until} ημέρες
Body: Include deadline date, what needs to be submitted
```

### 6.3 Template: Overdue Notice (Create)
```
Subject: Εκκρεμείς Υποχρεώσεις - {client_name}
Body: List of overdue obligations, contact info
```

### 6.4 Template: Document Upload Confirmation (Create)
```
Subject: Επιβεβαίωση Παραλαβής Εγγράφου
Body: Document name, upload date, next steps
```

---

## 7. Testing Strategy

### 7.1 Unit Tests Required

| Test | File | Priority |
|------|------|----------|
| `test_process_scheduled_emails` | test_tasks.py | HIGH |
| `test_check_deadline_reminders` | test_tasks.py | HIGH |
| `test_send_overdue_notifications` | test_tasks.py | MEDIUM |

### 7.2 Integration Tests

```bash
# Test email sending (use locmem backend)
python manage.py test accounting.tests.test_email_service -v 2

# Test with actual SMTP (manual)
python manage.py shell
>>> from accounting.services.email_service import EmailService
>>> EmailService.send_email('test@example.com', 'Test', '<p>Test</p>')
```

---

## 8. Deployment Checklist

### Pre-Deployment
- [ ] Create missing email templates in admin
- [ ] Configure `EMAIL_HOST_PASSWORD` in environment
- [ ] Test Redis connection
- [ ] Run migrations (if any model changes)

### Deployment
- [ ] Deploy code changes
- [ ] Restart Celery worker: `celery -A webcrm worker -l info`
- [ ] Restart Celery beat: `celery -A webcrm beat -l info`

### Post-Deployment
- [ ] Monitor Celery logs for task execution
- [ ] Check EmailLog for sent emails
- [ ] Verify scheduled emails are being processed

---

## 9. Summary & Recommendations

### What's Already Done (70%)
- Email models are complete and well-designed
- EmailService is production-ready
- Celery is properly configured
- Good test coverage exists
- HTML email template is professional

### What Needs Work (30%)
1. **Critical:** Add `process_scheduled_emails` task
2. **Critical:** Add `check_deadline_reminders` task
3. **High:** Create overdue notification workflow
4. **Medium:** Admin UI improvements

### Estimated Total Effort

| Phase | Effort | Description |
|-------|--------|-------------|
| Phase 1 | 5-6 hours | Critical gap fixes |
| Phase 2 | 3-4 hours | Overdue notifications |
| Phase 3 | 3-4 hours | Admin improvements |
| Testing | 2-3 hours | Full test suite |
| **Total** | **13-17 hours** | ~2 days of focused work |

### Recommended Order
1. Implement Phase 1 (critical gaps)
2. Add missing email templates via admin
3. Test with small batch of real clients
4. Implement Phase 2 (overdue notifications)
5. Implement Phase 3 (admin improvements)

---

## 10. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EMAIL AUTOMATION FLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRIGGERS                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ on_complete  │  │before_deadline│  │  on_overdue  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌────────────────────────────────────────────────┐        │
│  │           EmailAutomationRule                   │        │
│  │  - filter_obligation_types                      │        │
│  │  - template (FK)                                │        │
│  │  - timing (immediate/delay_1h/delay_24h)        │        │
│  └────────────────────────┬───────────────────────┘        │
│                           │                                 │
│         ┌─────────────────┴─────────────────┐              │
│         ▼                                   ▼              │
│  ┌──────────────┐                   ┌──────────────┐       │
│  │  IMMEDIATE   │                   │  SCHEDULED   │       │
│  │              │                   │              │       │
│  │ EmailService │                   │ScheduledEmail│       │
│  │ .send_email()│                   │   (queue)    │       │
│  └──────┬───────┘                   └──────┬───────┘       │
│         │                                  │               │
│         │                     ┌────────────┘               │
│         │                     ▼                            │
│         │          ┌──────────────────────┐                │
│         │          │process_scheduled_    │                │
│         │          │emails() [Celery]     │                │
│         │          └──────────┬───────────┘                │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌────────────────────────────────────────────────┐        │
│  │                   SMTP                          │        │
│  │              (smtp.gmail.com)                   │        │
│  └────────────────────────┬───────────────────────┘        │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────┐        │
│  │                  EmailLog                       │        │
│  │  - status: sent/failed/pending                  │        │
│  │  - error_message (if failed)                    │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Document created as part of LogistikoCRM development*
*Next Steps: Implement Phase 1 tasks*
