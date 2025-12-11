from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html

from crm.site.crmadminsite import crm_site
from settings.models import BannedCompanyName
from settings.models import MassmailSettings
from settings.models import PublicEmailDomain
from settings.models import Reminders
from settings.models import StopPhrase
from settings.models import BackupSettings, BackupHistory


class BannedCompanyNameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class MassmailSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "emails_per_day",
                    "use_business_time",
                    "business_time_start",
                    "business_time_end",
                    "unsubscribe_url",
                )
            },
        ),
    )

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(request.path + "1/change/")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PublicEmailDomainAdmin(admin.ModelAdmin):
    list_display = ('domain',)
    search_fields = ('domain',)


class RemindersAdmin(admin.ModelAdmin):

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(request.path + "1/change/")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StopPhraseAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
    list_display = ('phrase', 'last_occurrence_date')
    search_fields = ('phrase',)


crm_site.register(BannedCompanyName, BannedCompanyNameAdmin)
crm_site.register(PublicEmailDomain, PublicEmailDomainAdmin)
crm_site.register(StopPhrase, StopPhraseAdmin)

admin.site.register(BannedCompanyName, BannedCompanyNameAdmin)
admin.site.register(MassmailSettings, MassmailSettingsAdmin)
admin.site.register(PublicEmailDomain, PublicEmailDomainAdmin)
admin.site.register(Reminders, RemindersAdmin)
admin.site.register(StopPhrase, StopPhraseAdmin)


class BackupSettingsAdmin(admin.ModelAdmin):
    """Admin για ρυθμίσεις Backup - Singleton."""

    list_display = ['backup_path', 'include_media', 'max_backups', 'updated_at']
    fieldsets = (
        ('Ρυθμίσεις', {
            'fields': ('backup_path', 'include_media', 'max_backups')
        }),
    )

    def changelist_view(self, request, extra_context=None):
        # Redirect to singleton edit page
        BackupSettings.get_settings()  # Ensure exists
        return HttpResponseRedirect(request.path + "1/change/")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BackupHistoryAdmin(admin.ModelAdmin):
    """Admin για διαχείριση Backups."""

    list_display = [
        'filename_display', 'size_display', 'content_badges',
        'created_by', 'created_at_display', 'status_display', 'actions_display'
    ]
    list_filter = ['includes_db', 'includes_media', 'created_at']
    search_fields = ['filename', 'notes']
    readonly_fields = [
        'filename', 'file_path', 'file_size', 'includes_db', 'includes_media',
        'created_by', 'created_at', 'restored_at', 'restored_by', 'restore_mode'
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('Αρχείο', {
            'fields': ('filename', 'file_path', 'file_size', 'includes_db', 'includes_media')
        }),
        ('Δημιουργία', {
            'fields': ('created_by', 'created_at', 'notes')
        }),
        ('Επαναφορά', {
            'fields': ('restored_at', 'restored_by', 'restore_mode'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create/', self.admin_site.admin_view(self.create_backup_view), name='backup_create'),
            path('<int:pk>/download/', self.admin_site.admin_view(self.download_backup_view), name='backup_download'),
            path('<int:pk>/restore/', self.admin_site.admin_view(self.restore_backup_view), name='backup_restore'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_create_button'] = request.user.has_perm('settings.can_create_backup')
        return super().changelist_view(request, extra_context)

    # Custom views
    def create_backup_view(self, request):
        """Δημιουργία νέου backup."""
        if not request.user.has_perm('settings.can_create_backup'):
            messages.error(request, 'Δεν έχετε δικαίωμα δημιουργίας backup')
            return redirect('..')

        from .backup_utils import create_backup
        from .models import BackupSettings

        try:
            settings_obj = BackupSettings.get_settings()
            backup = create_backup(
                user=request.user,
                include_media=settings_obj.include_media,
                notes=f'Manual backup by {request.user.username}'
            )
            messages.success(request, f'Backup δημιουργήθηκε: {backup.filename} ({backup.file_size_display()})')
        except Exception as e:
            messages.error(request, f'Σφάλμα δημιουργίας backup: {e}')

        return redirect('..')

    def download_backup_view(self, request, pk):
        """Download backup file."""
        if not request.user.has_perm('settings.can_download_backup'):
            messages.error(request, 'Δεν έχετε δικαίωμα λήψης backup')
            return redirect('..')

        try:
            backup = BackupHistory.objects.get(pk=pk)
            if backup.file_exists():
                return FileResponse(
                    open(backup.file_path, 'rb'),
                    as_attachment=True,
                    filename=backup.filename
                )
            else:
                messages.error(request, 'Το αρχείο δεν βρέθηκε')
        except BackupHistory.DoesNotExist:
            messages.error(request, 'Backup not found')

        return redirect('..')

    def restore_backup_view(self, request, pk):
        """Restore backup - με επιλογή mode."""
        if not request.user.has_perm('settings.can_restore_backup'):
            messages.error(request, 'Δεν έχετε δικαίωμα επαναφοράς backup')
            return redirect('..')

        mode = request.GET.get('mode', 'replace')
        if mode not in ['replace', 'merge']:
            mode = 'replace'

        from .backup_utils import restore_backup

        try:
            success = restore_backup(pk, user=request.user, mode=mode)
            if success:
                mode_text = 'Αντικατάσταση' if mode == 'replace' else 'Συγχώνευση'
                messages.success(request, f'Backup επαναφέρθηκε ({mode_text})')
            else:
                messages.error(request, 'Αποτυχία επαναφοράς backup')
        except Exception as e:
            messages.error(request, f'Σφάλμα επαναφοράς: {e}')

        return redirect('..')

    # Display methods
    def filename_display(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-size: 12px;">{}</span>',
            obj.filename
        )
    filename_display.short_description = 'Αρχείο'

    def size_display(self, obj):
        return obj.file_size_display()
    size_display.short_description = 'Μέγεθος'

    def content_badges(self, obj):
        badges = []
        if obj.includes_db:
            badges.append('<span style="background:#3b82f6;color:white;padding:2px 6px;border-radius:4px;font-size:11px;">DB</span>')
        if obj.includes_media:
            badges.append('<span style="background:#10b981;color:white;padding:2px 6px;border-radius:4px;font-size:11px;">Media</span>')
        return format_html(' '.join(badges))
    content_badges.short_description = 'Περιεχόμενο'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = 'Ημ/νία'

    def status_display(self, obj):
        if not obj.file_exists():
            return format_html('<span style="color:#ef4444;">Αρχείο λείπει</span>')
        if obj.restored_at:
            return format_html('<span style="color:#6b7280;">Επαναφέρθηκε</span>')
        return format_html('<span style="color:#10b981;">Διαθέσιμο</span>')
    status_display.short_description = 'Κατάσταση'

    def actions_display(self, obj):
        if not obj.file_exists():
            return '-'
        return format_html(
            '<a href="{}download/" style="margin-right:8px;">Λήψη</a>'
            '<a href="{}restore/?mode=replace" onclick="return confirm(\'Αντικατάσταση υπαρχόντων δεδομένων;\')">Επαναφορά</a>',
            obj.pk, obj.pk
        )
    actions_display.short_description = 'Ενέργειες'

    def has_add_permission(self, request):
        return False  # Use custom create view


admin.site.register(BackupSettings, BackupSettingsAdmin)
admin.site.register(BackupHistory, BackupHistoryAdmin)
