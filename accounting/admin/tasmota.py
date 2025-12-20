# -*- coding: utf-8 -*-
"""
Tasmota Admin - Ρυθμίσεις IoT πόρτας

Singleton admin για τη διαχείριση της συσκευής Tasmota.
"""
import requests
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages

from ..models import TasmotaSettings, DoorAccessLog


@admin.register(TasmotaSettings)
class TasmotaSettingsAdmin(admin.ModelAdmin):
    """
    Admin για ρυθμίσεις Tasmota.
    Singleton - μόνο μία εγγραφή επιτρέπεται.
    """
    list_display = ['device_name', 'ip_address', 'port', 'is_enabled', 'connection_status', 'updated_at']
    readonly_fields = ['updated_at', 'connection_status_detail']

    fieldsets = (
        ('Συσκευή', {
            'fields': ('device_name', 'is_enabled'),
        }),
        ('Σύνδεση', {
            'fields': ('ip_address', 'port', 'timeout', 'connection_status_detail'),
        }),
        ('Πληροφορίες', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Επιτρέπει προσθήκη μόνο αν δεν υπάρχει εγγραφή"""
        return not TasmotaSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Δεν επιτρέπεται διαγραφή"""
        return False

    def connection_status(self, obj):
        """Εμφανίζει status σύνδεσης στη λίστα"""
        if not obj.is_enabled:
            return format_html('<span style="color: gray;">⏸ Απενεργοποιημένο</span>')

        try:
            response = requests.get(
                f"{obj.base_url}/cm?cmnd=Status",
                timeout=obj.timeout
            )
            if response.status_code == 200:
                return format_html('<span style="color: green;">✓ Online</span>')
            else:
                return format_html('<span style="color: red;">✗ Error {}</span>', response.status_code)
        except requests.exceptions.Timeout:
            return format_html('<span style="color: orange;">⏱ Timeout</span>')
        except requests.exceptions.ConnectionError:
            return format_html('<span style="color: red;">✗ Offline</span>')
        except Exception as e:
            return format_html('<span style="color: red;">✗ {}</span>', str(e)[:20])

    connection_status.short_description = 'Κατάσταση'

    def connection_status_detail(self, obj):
        """Αναλυτικό status σύνδεσης με test button"""
        if not obj or not obj.pk:
            return "Αποθηκεύστε πρώτα τις ρυθμίσεις"

        if not obj.is_enabled:
            return format_html(
                '<div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">'
                '<strong>⏸ Απενεργοποιημένο</strong><br>'
                'Ενεργοποιήστε τη συσκευή για να ελέγξετε τη σύνδεση.'
                '</div>'
            )

        try:
            response = requests.get(
                f"{obj.base_url}/cm?cmnd=Status",
                timeout=obj.timeout
            )
            if response.status_code == 200:
                data = response.json()
                status = data.get('Status', {})
                device_name = status.get('DeviceName', 'Unknown')
                power = status.get('Power', 0)

                return format_html(
                    '<div style="padding: 10px; background: #d4edda; border-radius: 5px;">'
                    '<strong style="color: green;">✓ Συνδέθηκε επιτυχώς!</strong><br>'
                    'Device: {}<br>'
                    'Power: {}<br>'
                    'URL: <code>{}</code>'
                    '</div>',
                    device_name,
                    'ON' if power else 'OFF',
                    obj.base_url
                )
            else:
                return format_html(
                    '<div style="padding: 10px; background: #f8d7da; border-radius: 5px;">'
                    '<strong style="color: red;">✗ Σφάλμα HTTP {}</strong>'
                    '</div>',
                    response.status_code
                )
        except requests.exceptions.Timeout:
            return format_html(
                '<div style="padding: 10px; background: #fff3cd; border-radius: 5px;">'
                '<strong style="color: orange;">⏱ Timeout</strong><br>'
                'Η συσκευή δεν απάντησε σε {} δευτερόλεπτα.<br>'
                'Ελέγξτε την IP: <code>{}</code>'
                '</div>',
                obj.timeout,
                obj.base_url
            )
        except requests.exceptions.ConnectionError:
            return format_html(
                '<div style="padding: 10px; background: #f8d7da; border-radius: 5px;">'
                '<strong style="color: red;">✗ Αδυναμία σύνδεσης</strong><br>'
                'Δεν βρέθηκε η συσκευή στη διεύθυνση: <code>{}</code><br>'
                'Ελέγξτε ότι η IP είναι σωστή και η συσκευή είναι στο δίκτυο.'
                '</div>',
                obj.base_url
            )
        except Exception as e:
            return format_html(
                '<div style="padding: 10px; background: #f8d7da; border-radius: 5px;">'
                '<strong style="color: red;">✗ Σφάλμα</strong><br>'
                '{}'
                '</div>',
                str(e)
            )

    connection_status_detail.short_description = 'Έλεγχος Σύνδεσης'


@admin.register(DoorAccessLog)
class DoorAccessLogAdmin(admin.ModelAdmin):
    """Admin για logs πρόσβασης πόρτας"""
    list_display = ['timestamp', 'user', 'action', 'result', 'ip_address']
    list_filter = ['action', 'result', 'timestamp']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['user', 'action', 'result', 'ip_address', 'user_agent', 'response_data', 'timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        """Logs δημιουργούνται αυτόματα"""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs δεν μπορούν να τροποποιηθούν"""
        return False
