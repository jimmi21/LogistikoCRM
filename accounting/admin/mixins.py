# -*- coding: utf-8 -*-
"""
Shared admin mixins and inline classes for accounting app.
"""
import os

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, escape

from ..models import (
    VoIPCall,
    ClientDocument,
    EmailLog,
)


# ============================================================================
# INLINES - VoIP Call History for ClientProfile
# ============================================================================

class VoIPCallInline(admin.TabularInline):
    """Inline για εμφάνιση ιστορικού κλήσεων στην καρτέλα πελάτη"""
    model = VoIPCall
    extra = 0
    max_num = 0  # No adding from here
    can_delete = False
    fields = ['started_at', 'direction', 'status', 'duration_display', 'resolution', 'notes']
    readonly_fields = ['started_at', 'direction', 'status', 'duration_display', 'resolution']
    ordering = ['-started_at']
    verbose_name = 'Κλήση'
    verbose_name_plural = '📞 Ιστορικό Κλήσεων'

    def duration_display(self, obj):
        if obj.duration_seconds:
            mins, secs = divmod(obj.duration_seconds, 60)
            return f"{mins}:{secs:02d}"
        return "-"
    duration_display.short_description = 'Διάρκεια'

    def has_add_permission(self, request, obj=None):
        return False


class ClientProfileDocumentInline(admin.TabularInline):
    """Inline για όλα τα documents ενός πελάτη"""
    model = ClientDocument
    extra = 0
    fields = ['document_category', 'file', 'filename', 'uploaded_at', 'obligation']
    readonly_fields = ['filename', 'uploaded_at']
    ordering = ['-uploaded_at']
    verbose_name = 'Έγγραφο'
    verbose_name_plural = 'Έγγραφα Πελάτη'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('obligation', 'obligation__obligation_type')


class ClientDocumentInline(admin.TabularInline):
    """Inline για documents στο MonthlyObligation detail view"""
    model = ClientDocument
    extra = 1
    fields = ['document_category', 'file', 'description']
    verbose_name = 'Έγγραφο'
    verbose_name_plural = '📎 Συνημμένα Έγγραφα'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client')


class EmailLogInline(admin.TabularInline):
    """Inline view of sent emails for obligations"""
    model = EmailLog
    fk_name = 'obligation'
    extra = 0
    max_num = 10
    readonly_fields = ['sent_at', 'recipient_email', 'subject', 'status_badge', 'sent_by', 'view_body_link']
    fields = ['sent_at', 'recipient_email', 'subject', 'status_badge', 'sent_by', 'view_body_link']
    ordering = ['-sent_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

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
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Κατάσταση'

    def view_body_link(self, obj):
        return format_html(
            '<a href="{}">👁️ View</a>',
            reverse('admin:accounting_emaillog_change', args=[obj.pk])
        )
    view_body_link.short_description = 'Περιεχόμενο'
