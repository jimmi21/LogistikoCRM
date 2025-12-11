# -*- coding: utf-8 -*-
"""
Email-related admin classes for accounting app.

Contains:
- EmailTemplateAdmin
- EmailAutomationRuleAdmin
- ScheduledEmailAdmin
- EmailLogAdmin
"""
from django import forms
from django.urls import reverse
from django.utils.html import format_html, escape
from django.contrib import admin
from django.contrib import messages
from django.db.models import Count

from ..models import (
    EmailTemplate,
    EmailAutomationRule,
    ScheduledEmail,
    EmailLog,
)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'obligation_type', 'is_active', 'created_at', 'preview_button']
    list_filter = ['is_active', 'obligation_type', 'created_at']
    search_fields = ['name', 'subject', 'body_html']
    autocomplete_fields = ['obligation_type']

    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Αυτόματη Επιλογή', {
            'fields': ('obligation_type',),
            'description': 'Αν οριστεί τύπος υποχρέωσης, αυτό το template θα επιλέγεται αυτόματα για εκείνον τον τύπο.'
        }),
        ('Περιεχόμενο Email', {
            'fields': ('subject', 'body_html'),
            'description': '''
            <strong style="color: #667eea;">Διαθέσιμες Μεταβλητές (χρήση: {variable}):</strong><br><br>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px;">
            <strong>Πελάτης:</strong><br>
            • <code>{client_name}</code> - Επωνυμία πελάτη<br>
            • <code>{client_afm}</code> - ΑΦΜ<br>
            • <code>{client_email}</code> - Email<br><br>
            <strong>Υποχρέωση:</strong><br>
            • <code>{obligation_type}</code> - Τύπος υποχρέωσης<br>
            • <code>{period_month}</code> - Μήνας περιόδου (01-12)<br>
            • <code>{period_year}</code> - Έτος περιόδου<br>
            • <code>{period_display}</code> - Περίοδος (π.χ. 01/2025)<br>
            • <code>{deadline}</code> - Προθεσμία (ημ/νία)<br>
            • <code>{completed_date}</code> - Ημερομηνία ολοκλήρωσης<br><br>
            <strong>Εταιρεία:</strong><br>
            • <code>{accountant_name}</code> - Το όνομά σας<br>
            • <code>{company_name}</code> - Όνομα εταιρείας
            </div>
            '''
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related for ForeignKey fields"""
        qs = super().get_queryset(request)
        return qs.select_related('obligation_type')

    def preview_button(self, obj):
        return format_html(
            '<a class="button" href="{}">👁️ Preview</a>',
            f'/accounting/email-template/{obj.pk}/preview/'
        )
    preview_button.short_description = 'Προεπισκόπηση'


@admin.register(EmailAutomationRule)
class EmailAutomationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger', 'template', 'timing', 'is_active', 'created_at']
    list_filter = ['is_active', 'trigger', 'timing']
    search_fields = ['name', 'description']
    filter_horizontal = ['filter_obligation_types']

    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Trigger & Filters', {
            'fields': ('trigger', 'filter_obligation_types'),
            'description': '⚙️ Πότε θα ενεργοποιείται ο κανόνας και για ποιους τύπους υποχρεώσεων'
        }),
        ('Email Template', {
            'fields': ('template',)
        }),
        ('Χρονοπρογραμματισμός', {
            'fields': ('timing', 'scheduled_time', 'days_before_deadline'),
            'description': '⏰ Πότε θα αποστέλλεται το email'
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related for ForeignKey fields"""
        qs = super().get_queryset(request)
        return qs.select_related('template')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        status = "ενημερώθηκε" if change else "δημιουργήθηκε"
        messages.success(request, f'✅ Ο κανόνας "{obj.name}" {status} επιτυχώς!')


@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = [
        'recipients_display',
        'recipient_count_display',
        'subject_preview',
        'send_at',
        'status',
        'obligations_count',
        'actions_column'
    ]
    list_filter = ['status', 'send_at', 'created_at']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
    filter_horizontal = ['obligations']
    readonly_fields = ['sent_at', 'error_message', 'created_by', 'created_at', 'recipient_count_readonly']

    fieldsets = (
        ('Παραλήπτες', {
            'fields': ('recipient_email', 'recipient_name', 'recipient_count_readonly', 'client'),
            'description': '📧 Πολλαπλά emails χωρισμένα με κόμμα ή νέα γραμμή. '
                           'Για bulk emails, όλοι οι παραλήπτες θα λάβουν το email μέσω BCC.'
        }),
        ('Email Content', {
            'fields': ('subject', 'body_html', 'template', 'automation_rule')
        }),
        ('Υποχρεώσεις', {
            'fields': ('obligations',),
            'description': '📎 Τα attachments θα προστεθούν αυτόματα από τις υποχρεώσεις'
        }),
        ('Χρονοπρογραμματισμός', {
            'fields': ('send_at', 'sent_at', 'status', 'error_message')
        }),
        ('Μεταδεδομένα', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['send_now', 'cancel_emails']

    def get_queryset(self, request):
        """Optimize queries with select_related, prefetch_related and Count annotation"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'client', 'template', 'automation_rule', 'created_by'
        ).prefetch_related('obligations').annotate(
            _obligations_count=Count('obligations')
        )

    def get_form(self, request, obj=None, **kwargs):
        """Override to use textarea widget for recipient_email field"""
        form = super().get_form(request, obj, **kwargs)
        if 'recipient_email' in form.base_fields:
            form.base_fields['recipient_email'].widget = forms.Textarea(attrs={
                'rows': 4,
                'cols': 60,
                'placeholder': 'email1@example.com, email2@example.com\nή ένα email ανά γραμμή'
            })
            form.base_fields['recipient_email'].help_text = (
                'Πολλαπλά emails χωρισμένα με κόμμα (,) ή νέα γραμμή. '
                'Για bulk αποστολή, όλοι λαμβάνουν μέσω BCC.'
            )
        if 'recipient_name' in form.base_fields:
            form.base_fields['recipient_name'].widget = forms.Textarea(attrs={
                'rows': 2,
                'cols': 60,
                'placeholder': 'Όνομα 1, Όνομα 2 (προαιρετικό)'
            })
        return form

    def recipients_display(self, obj):
        """Display recipients summary"""
        return obj.get_recipients_display()
    recipients_display.short_description = 'Παραλήπτες'

    def recipient_count_display(self, obj):
        """Display recipient count with icon"""
        count = obj.recipient_count
        if count == 1:
            return format_html('👤 1')
        elif count > 1:
            return format_html('👥 {} (BCC)', count)
        return format_html('<span style="color: #dc2626;">⚠️ 0</span>')
    recipient_count_display.short_description = 'Αριθμός'

    def recipient_count_readonly(self, obj):
        """Readonly field showing recipient count"""
        count = obj.recipient_count
        recipients = obj.get_recipients_list()
        if count == 0:
            return format_html('<span style="color: #dc2626;">⚠️ Δεν βρέθηκαν έγκυρα emails</span>')
        elif count == 1:
            return format_html('👤 1 παραλήπτης: {}', recipients[0])
        else:
            return format_html('👥 {} παραλήπτες (θα σταλούν μέσω BCC)', count)
    recipient_count_readonly.short_description = 'Πλήθος Παραληπτών'

    def subject_preview(self, obj):
        preview = escape(obj.subject[:50])
        if len(obj.subject) > 50:
            preview += '...'
        return preview
    subject_preview.short_description = 'Θέμα'

    def obligations_count(self, obj):
        # Use annotated count to avoid N+1
        count = getattr(obj, '_obligations_count', None)
        if count is None:
            count = obj.obligations.count()
        attachments = obj.get_attachments()
        return format_html(
            '{} υποχρεώσεις<br><small>📎 {} αρχεία</small>',
            count,
            len(attachments)
        )
    obligations_count.short_description = 'Περιεχόμενο'

    def actions_column(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="#" onclick="sendNow({})">🚀 Αποστολή Τώρα</a> '
                '<a class="button" href="#" onclick="cancelEmail({})">🚫 Ακύρωση</a>',
                obj.pk, obj.pk
            )
        elif obj.status == 'sent':
            return '✅ Στάλθηκε'
        elif obj.status == 'failed':
            return format_html('❌ <a href="#" title="{}">Σφάλμα</a>', obj.error_message)
        return '—'
    actions_column.short_description = 'Ενέργειες'

    @admin.action(description='🚀 Αποστολή Τώρα')
    def send_now(self, request, queryset):
        try:
            from accounting.services.email_service import send_scheduled_email

            sent = 0
            failed = 0

            for email in queryset.filter(status='pending'):
                try:
                    send_scheduled_email(email.pk)
                    sent += 1
                except Exception as e:
                    failed += 1
                    email.mark_as_failed(str(e))

            if sent:
                messages.success(request, f'✅ Στάλθηκαν {sent} emails!')
            if failed:
                messages.error(request, f'❌ Απέτυχαν {failed} emails!')
        except ImportError:
            messages.error(request, '❌ Το email service δεν είναι διαθέσιμο')

    @admin.action(description='🚫 Ακύρωση')
    def cancel_emails(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='cancelled')
        messages.success(request, f'🚫 Ακυρώθηκαν {updated} emails!')

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin for viewing sent email history"""
    list_display = [
        'sent_at_formatted',
        'recipient_info',
        'subject_preview',
        'status_badge',
        'template_used',
        'sent_by',
        'client_link'
    ]
    list_filter = ['status', 'sent_at', 'template_used', 'sent_by']
    search_fields = [
        'recipient_email',
        'recipient_name',
        'subject',
        'client__eponimia',
        'client__afm'
    ]
    readonly_fields = [
        'recipient_email',
        'recipient_name',
        'client',
        'obligation',
        'template_used',
        'subject',
        'body',
        'status',
        'error_message',
        'sent_at',
        'sent_by'
    ]
    ordering = ['-sent_at']
    list_per_page = 50
    date_hierarchy = 'sent_at'

    def get_queryset(self, request):
        """Optimize queries with select_related for ForeignKey fields"""
        qs = super().get_queryset(request)
        return qs.select_related('client', 'sent_by', 'obligation')

    fieldsets = (
        ('Παραλήπτης', {
            'fields': ('recipient_name', 'recipient_email', 'client')
        }),
        ('Περιεχόμενο Email', {
            'fields': ('subject', 'body'),
            'classes': ('wide',)
        }),
        ('Μεταδεδομένα', {
            'fields': ('template_used', 'obligation', 'sent_by', 'sent_at')
        }),
        ('Κατάσταση', {
            'fields': ('status', 'error_message'),
            'classes': ('collapse',) if True else ()
        }),
    )

    def has_add_permission(self, request):
        # Email logs are created by the system, not manually
        return False

    def has_change_permission(self, request, obj=None):
        # Logs should be read-only
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow superusers to delete old logs
        return request.user.is_superuser

    def sent_at_formatted(self, obj):
        return obj.sent_at.strftime('%d/%m/%Y %H:%M')
    sent_at_formatted.short_description = 'Αποστολή'
    sent_at_formatted.admin_order_field = 'sent_at'

    def recipient_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            escape(obj.recipient_name),
            obj.recipient_email
        )
    recipient_info.short_description = 'Παραλήπτης'

    def subject_preview(self, obj):
        subject = escape(obj.subject)
        if len(obj.subject) > 50:
            return subject[:50] + '...'
        return subject
    subject_preview.short_description = 'Θέμα'

    def status_badge(self, obj):
        colors = {
            'sent': '#10b981',
            'failed': '#ef4444',
            'pending': '#f59e0b'
        }
        icons = {
            'sent': '✅',
            'failed': '❌',
            'pending': '⏳'
        }
        color = colors.get(obj.status, '#666')
        icon = icons.get(obj.status, '?')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Κατάσταση'
    status_badge.admin_order_field = 'status'

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounting_clientprofile_change', args=[obj.client.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, escape(obj.client.eponimia)
            )
        return '—'
    client_link.short_description = 'Πελάτης'
