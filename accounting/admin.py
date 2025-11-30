from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core.management import call_command
from django import forms
from django.utils import timezone
from .export_import import export_clients_to_excel, export_clients_summary_to_excel  # ✅ ΔΙΟΡΘΩΣΗ
import io
import os
import csv
import tempfile
from datetime import datetime
from django.core.management import call_command
from django.http import HttpResponse
import logging

from .models import (
    ClientProfile, 
    ObligationGroup, 
    ObligationProfile, 
    ObligationType,
    ClientObligation,
    MonthlyObligation,
    EmailTemplate,
    EmailAutomationRule,
    ScheduledEmail,
    VoIPCall,
    VoIPCallLog,
    Ticket,
    ClientDocument,
    ArchiveConfiguration
)

logger = logging.getLogger(__name__)


# ============================================================================
# FORMS
# ============================================================================

class GenerateObligationsForm(forms.Form):
    year = forms.IntegerField(
        label='Έτος',
        initial=timezone.now().year,
        help_text='Έτος για το οποίο θα δημιουργηθούν οι υποχρεώσεις'
    )
    month = forms.IntegerField(
        label='Μήνας',
        initial=timezone.now().month,
        min_value=1,
        max_value=12,
        help_text='Μήνας (1-12)'
    )


class BulkAssignForm(forms.Form):
    clients = forms.ModelMultipleChoiceField(
        queryset=ClientProfile.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Πελάτες', False),
        label='Επιλογή Πελατών',
        required=True
    )
    obligation_profiles = forms.ModelMultipleChoiceField(
        queryset=ObligationProfile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Profiles Υποχρεώσεων',
        required=False
    )
    obligation_types = forms.ModelMultipleChoiceField(
        queryset=ObligationType.objects.filter(profile__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label='Μεμονωμένες Υποχρεώσεις',
        required=False
    )


class ClientObligationForm(forms.ModelForm):
    """Custom form με validation για ΦΠΑ και όλα τα exclusion groups"""
    class Meta:
        model = ClientObligation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        obligation_types = cleaned_data.get('obligation_types')

        if obligation_types:
            # ✅ ENHANCED VALIDATION: Έλεγχος για όλα τα exclusion groups
            exclusion_groups = {}
            for obl_type in obligation_types:
                if obl_type.exclusion_group:
                    group_name = obl_type.exclusion_group.name
                    if group_name not in exclusion_groups:
                        exclusion_groups[group_name] = []
                    exclusion_groups[group_name].append(obl_type.name)

            # Αν υπάρχει group με >1 υποχρέωση, error
            for group_name, type_names in exclusion_groups.items():
                if len(type_names) > 1:
                    raise forms.ValidationError(
                        f'❌ Δεν μπορείτε να επιλέξετε ταυτόχρονα: {", ".join(type_names)} '
                        f'(ανήκουν στην ομάδα αλληλοαποκλεισμού "{group_name}")'
                    )

            # Legacy ΦΠΑ validation (για backward compatibility)
            type_names = [t.name for t in obligation_types]
            has_monthly = any('ΦΠΑ Μηνιαίο' in name or 'ΦΠΑ ΜΗΝΙΑΙΟ' in name.upper() for name in type_names)
            has_quarterly = any('ΦΠΑ Τρίμηνο' in name or 'ΦΠΑ ΤΡΙΜΗΝΟ' in name.upper() for name in type_names)

            if has_monthly and has_quarterly:
                raise forms.ValidationError(
                    '❌ Δεν μπορείτε να επιλέξετε ταυτόχρονα ΦΠΑ Μηνιαίο και ΦΠΑ Τρίμηνο!'
                )

        return cleaned_data


class ObligationGroupForm(forms.ModelForm):
    """Custom form για ObligationGroup με checkboxes"""
    obligation_types = forms.ModelMultipleChoiceField(
        queryset=ObligationType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Υποχρεώσεις στην Ομάδα',
        help_text='Επιλέξτε τις υποχρεώσεις που ανήκουν σε αυτήν την ομάδα αλληλοαποκλεισμού'
    )
    
    class Meta:
        model = ObligationGroup
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['obligation_types'] = self.instance.obligationtype_set.all()


class ObligationProfileForm(forms.ModelForm):
    """Custom form για ObligationProfile με checkboxes"""
    obligation_types = forms.ModelMultipleChoiceField(
        queryset=ObligationType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Υποχρεώσεις στο Profile',
        help_text='Επιλέξτε τις υποχρεώσεις που ενεργοποιούνται μαζί με αυτό το profile'
    )
    
    class Meta:
        model = ObligationProfile
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['obligation_types'] = self.instance.obligations.all()


# ============================================================================
# ADMIN CLASSES - CLIENT PROFILE (ENHANCED)
# ============================================================================

from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core.management import call_command
from django import forms
from django.utils import timezone
from .export_import import export_clients_to_excel, export_clients_summary_to_excel  # ✅ ΔΙΟΡΘΩΣΗ
import io
import os
import csv
import tempfile
from datetime import datetime
from django.core.management import call_command
from django.http import HttpResponse
import logging

from .models import (
    ClientProfile, 
    ObligationGroup, 
    ObligationProfile, 
    ObligationType,
    ClientObligation,
    MonthlyObligation,
    EmailTemplate,
    EmailAutomationRule,
    ScheduledEmail,
    VoIPCall,
    VoIPCallLog,
    Ticket,
    ClientDocument,
    ArchiveConfiguration
)

logger = logging.getLogger(__name__)


# ============================================================================
# FORMS
# ============================================================================

class GenerateObligationsForm(forms.Form):
    year = forms.IntegerField(
        label='Έτος',
        initial=timezone.now().year,
        help_text='Έτος για το οποίο θα δημιουργηθούν οι υποχρεώσεις'
    )
    month = forms.IntegerField(
        label='Μήνας',
        initial=timezone.now().month,
        min_value=1,
        max_value=12,
        help_text='Μήνας (1-12)'
    )


class BulkAssignForm(forms.Form):
    clients = forms.ModelMultipleChoiceField(
        queryset=ClientProfile.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Πελάτες', False),
        label='Επιλογή Πελατών',
        required=True
    )
    obligation_profiles = forms.ModelMultipleChoiceField(
        queryset=ObligationProfile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Profiles Υποχρεώσεων',
        required=False
    )
    obligation_types = forms.ModelMultipleChoiceField(
        queryset=ObligationType.objects.filter(profile__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label='Μεμονωμένες Υποχρεώσεις',
        required=False
    )


class ClientObligationForm(forms.ModelForm):
    """Custom form με validation για ΦΠΑ και όλα τα exclusion groups"""
    class Meta:
        model = ClientObligation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        obligation_types = cleaned_data.get('obligation_types')

        if obligation_types:
            # ✅ ENHANCED VALIDATION: Έλεγχος για όλα τα exclusion groups
            exclusion_groups = {}
            for obl_type in obligation_types:
                if obl_type.exclusion_group:
                    group_name = obl_type.exclusion_group.name
                    if group_name not in exclusion_groups:
                        exclusion_groups[group_name] = []
                    exclusion_groups[group_name].append(obl_type.name)

            # Αν υπάρχει group με >1 υποχρέωση, error
            for group_name, type_names in exclusion_groups.items():
                if len(type_names) > 1:
                    raise forms.ValidationError(
                        f'❌ Δεν μπορείτε να επιλέξετε ταυτόχρονα: {", ".join(type_names)} '
                        f'(ανήκουν στην ομάδα αλληλοαποκλεισμού "{group_name}")'
                    )

            # Legacy ΦΠΑ validation (για backward compatibility)
            type_names = [t.name for t in obligation_types]
            has_monthly = any('ΦΠΑ Μηνιαίο' in name or 'ΦΠΑ ΜΗΝΙΑΙΟ' in name.upper() for name in type_names)
            has_quarterly = any('ΦΠΑ Τρίμηνο' in name or 'ΦΠΑ ΤΡΙΜΗΝΟ' in name.upper() for name in type_names)

            if has_monthly and has_quarterly:
                raise forms.ValidationError(
                    '❌ Δεν μπορείτε να επιλέξετε ταυτόχρονα ΦΠΑ Μηνιαίο και ΦΠΑ Τρίμηνο!'
                )

        return cleaned_data


class ObligationGroupForm(forms.ModelForm):
    """Custom form για ObligationGroup με checkboxes"""
    obligation_types = forms.ModelMultipleChoiceField(
        queryset=ObligationType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Υποχρεώσεις στην Ομάδα',
        help_text='Επιλέξτε τις υποχρεώσεις που ανήκουν σε αυτήν την ομάδα αλληλοαποκλεισμού'
    )
    
    class Meta:
        model = ObligationGroup
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['obligation_types'] = self.instance.obligationtype_set.all()


class ObligationProfileForm(forms.ModelForm):
    """Custom form για ObligationProfile με checkboxes"""
    obligation_types = forms.ModelMultipleChoiceField(
        queryset=ObligationType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Υποχρεώσεις στο Profile',
        help_text='Επιλέξτε τις υποχρεώσεις που ενεργοποιούνται μαζί με αυτό το profile'
    )
    
    class Meta:
        model = ObligationProfile
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['obligation_types'] = self.instance.obligations.all()


# ============================================================================
# ADMIN CLASSES - CLIENT PROFILE (ENHANCED)
# ============================================================================

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):  # ✅ ΔΙΟΡΘΩΣΗ: Προστέθηκε το όνομα της κλάσης!
    list_display = [
        'afm',
        'eponimia',
        'eidos_ipoxreou',
        'katigoria_vivlion',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'eidos_ipoxreou',
        'katigoria_vivlion',
        'agrotis',
        'is_active'
    ]
    
    search_fields = [
        'afm',
        'eponimia',
        'onoma',
        'email',
        'kinito_tilefono',
        'tilefono_oikias_1',
        'tilefono_epixeirisis_1',
        'doy'
    ]
    
    list_editable = ['is_active']
    
    actions = [
        'export_selected',
        'export_all',
        'export_summary',  # ✅ ΝΕΟ
        'export_to_csv',
        'mark_active',
        'mark_inactive',
    ]
    
    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields': ('afm', 'doy', 'eponimia', 'onoma', 'onoma_patros', 'is_active')
        }),
        ('Ταυτοποίηση', {
            'fields': ('arithmos_taftotitas', 'eidos_taftotitas', 'prosopikos_arithmos', 
                      'amka', 'am_ika', 'arithmos_gemi', 'arithmos_dypa'),
            'classes': ('collapse',)
        }),
        ('Προσωπικά Στοιχεία', {
            'fields': ('imerominia_gennisis', 'imerominia_gamou', 'filo'),
            'classes': ('collapse',)
        }),
        ('Διεύθυνση Κατοικίας', {
            'fields': ('diefthinsi_katoikias', 'arithmos_katoikias', 'poli_katoikias', 
                      'dimos_katoikias', 'nomos_katoikias', 'tk_katoikias',
                      'tilefono_oikias_1', 'tilefono_oikias_2', 'kinito_tilefono'),
            'classes': ('collapse',)
        }),
        ('Διεύθυνση Επιχείρησης', {
            'fields': ('diefthinsi_epixeirisis', 'arithmos_epixeirisis', 'poli_epixeirisis',
                      'dimos_epixeirisis', 'nomos_epixeirisis', 'tk_epixeirisis',
                      'tilefono_epixeirisis_1', 'tilefono_epixeirisis_2', 'email'),
            'classes': ('collapse',)
        }),
        ('Τραπεζικά', {
            'fields': ('trapeza', 'iban'),
            'classes': ('collapse',)
        }),
        ('Επιχειρηματικά', {
            'fields': ('eidos_ipoxreou', 'katigoria_vivlion', 'nomiki_morfi', 
                      'agrotis', 'imerominia_enarksis')
        }),
        ('Διαπιστευτήρια', {
            'fields': ('onoma_xristi_taxisnet', 'kodikos_taxisnet',
                      'onoma_xristi_ika_ergodoti', 'kodikos_ika_ergodoti',
                      'onoma_xristi_gemi', 'kodikos_gemi'),
            'classes': ('collapse',)
        }),
        ('Λοιπά', {
            'fields': ('afm_sizigou', 'afm_foreas', 'am_klidi'),
            'classes': ('collapse',)
        }),
    )
    
    # ============================================
    # ENHANCED AUTOCOMPLETE SEARCH
    # ============================================
    
    def get_search_results(self, request, queryset, search_term):
        """
        Βελτιωμένο search για autocomplete με smart matching
        """
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        
        if not search_term:
            return queryset, use_distinct
        
        from django.db.models import Q
        
        search_term_clean = search_term.strip()
        
        if search_term_clean.isdigit():
            phone_search = self.model.objects.filter(
                Q(afm__icontains=search_term_clean) |
                Q(kinito_tilefono__icontains=search_term_clean) |
                Q(tilefono_oikias_1__icontains=search_term_clean) |
                Q(tilefono_oikias_2__icontains=search_term_clean) |
                Q(tilefono_epixeirisis_1__icontains=search_term_clean) |
                Q(tilefono_epixeirisis_2__icontains=search_term_clean)
            )
            queryset |= phone_search
            use_distinct = True
        
        elif '@' in search_term_clean:
            email_search = self.model.objects.filter(
                Q(email__icontains=search_term_clean)
            )
            queryset |= email_search
            use_distinct = True
        
        else:
            text_search = self.model.objects.filter(
                Q(eponimia__icontains=search_term_clean) |
                Q(onoma__icontains=search_term_clean) |
                Q(onoma_patros__icontains=search_term_clean) |
                Q(doy__icontains=search_term_clean) |
                Q(poli_katoikias__icontains=search_term_clean) |
                Q(poli_epixeirisis__icontains=search_term_clean)
            )
            queryset |= text_search
            use_distinct = True
        
        return queryset, use_distinct
    
    # ============================================
    # ✅ EXPORT ACTIONS - ΧΡΗΣΙΜΟΠΟΙΟΥΝ ΤΟ export_import MODULE
    # ============================================
    
    def export_selected(self, request, queryset):
        """Export επιλεγμένων πελατών με ΟΛΑ τα πεδία (52 fields)"""
        return export_clients_to_excel(queryset)
    export_selected.short_description = '📥 Export Επιλεγμένων (Πλήρες - 52 πεδία)'
    
    def export_all(self, request, queryset):
        """Export όλων των πελατών με ΟΛΑ τα πεδία (52 fields)"""
        return export_clients_to_excel()  # No queryset = όλοι
    export_all.short_description = '📥 Export ΟΛΩΝ (Πλήρες - 52 πεδία)'
    
    def export_summary(self, request, queryset):
        """Export συνοπτικής λίστας (11 basic fields)"""
        return export_clients_summary_to_excel(queryset)
    export_summary.short_description = '📄 Export Επιλεγμένων (Σύνοψη - 11 πεδία)'
    
    def export_to_csv(self, request, queryset):
        """Export to CSV - Enhanced με περισσότερα πεδία"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="clients_{datetime.now().strftime("%Y%m%d")}.csv"'
    
        writer = csv.writer(response)
    
        # ✅ ENHANCED HEADERS - 25 πεδία αντί για 11
        writer.writerow([
            'ΑΦΜ',
            'ΔΟΥ',
            'Επωνυμία',
            'Όνομα',
            'Όνομα Πατρός',
            'Είδος Υπόχρεου',
            'Κατηγορία Βιβλίων',
            'Νομική Μορφή',
            'Αγρότης',
            'Email',
            'Κινητό',
            'Τηλ. Οικίας',
            'Τηλ. Επιχείρησης',
            'Διεύθυνση Κατοικίας',
            'Πόλη Κατοικίας',
            'ΤΚ Κατοικίας',
            'Διεύθυνση Επιχείρησης',
            'Πόλη Επιχείρησης',
            'ΤΚ Επιχείρησης',
            'Τράπεζα',
            'IBAN',
            'ΑΜΚΑ',
            'ΑΜ ΙΚΑ',
            'Ενεργός',
            'Δημιουργήθηκε'
        ])
    
        for client in queryset.select_related():
            writer.writerow([
                client.afm,
                client.doy or '',
                client.eponimia,
                client.onoma or '',
                client.onoma_patros or '',
                client.get_eidos_ipoxreou_display(),
                client.get_katigoria_vivlion_display() if client.katigoria_vivlion else '',
                client.nomiki_morfi or '',
                'ΝΑΙ' if client.agrotis else 'ΟΧΙ',
                client.email or '',
                client.kinito_tilefono or '',
                client.tilefono_oikias_1 or '',
                client.tilefono_epixeirisis_1 or '',
                client.diefthinsi_katoikias or '',
                client.poli_katoikias or '',
                client.tk_katoikias or '',
                client.diefthinsi_epixeirisis or '',
                client.poli_epixeirisis or '',
                client.tk_epixeirisis or '',
                client.trapeza or '',
                client.iban or '',
                client.amka or '',
                client.am_ika or '',
                'Ναι' if client.is_active else 'Όχι',
                client.created_at.strftime('%d/%m/%Y %H:%M') if client.created_at else ''
            ])
    
        self.message_user(request, f'✅ Εξήχθησαν {queryset.count()} πελάτες σε CSV (25 πεδία)', messages.SUCCESS)
        return response
    export_to_csv.short_description = '📊 Export σε CSV'    


    def mark_active(self, request, queryset):
        """Ενεργοποίηση πελατών"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Ενεργοποιήθηκαν {updated} πελάτες', messages.SUCCESS)
    mark_active.short_description = '✅ Ενεργοποίηση'
    
    def mark_inactive(self, request, queryset):
        """Απενεργοποίηση πελατών"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'⚠️ Απενεργοποιήθηκαν {updated} πελάτες', messages.WARNING)
    mark_inactive.short_description = '❌ Απενεργοποίηση'
    
    # ============================================
    # CUSTOM URLS
    # ============================================
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.admin_site.admin_view(self.import_view), 
                 name='accounting_clientprofile_import'),
            path('download-template/', self.admin_site.admin_view(self.download_template), 
                 name='accounting_clientprofile_template'),
            path('mass-update/', self.admin_site.admin_view(self.mass_update_view),
                 name='accounting_clientprofile_mass_update'),
        ]
        return custom_urls + urls
    
    def import_view(self, request):
        """Import view για Excel"""
        if request.method == 'POST' and 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                for chunk in excel_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            
            try:
                out = io.StringIO()
                call_command('import_clients', tmp_path, stdout=out)
                
                output = out.getvalue()
                
                if '✅' in output or 'Ολοκληρώθηκε' in output:
                    messages.success(request, output)
                else:
                    messages.warning(request, output)
                    
            except Exception as e:
                messages.error(request, f'❌ Σφάλμα: {str(e)}')
            finally:
                os.unlink(tmp_path)
            
            return redirect('..')
        
        context = {
            'title': 'Import Πελατών από Excel',
            'has_permission': True,
        }
        return render(request, 'admin/accounting/import_clients.html', context)
    
    def download_template(self, request):
        """Download template Excel"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp_path = tmp.name
            
            call_command('create_excel_template', tmp_path)
            
            with open(tmp_path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="Template_Pelaton_{datetime.now().strftime("%Y%m%d")}.xlsx"'
            
            os.unlink(tmp_path)
            return response
            
        except Exception as e:
            messages.error(request, f'❌ Σφάλμα: {str(e)}')
            return redirect('..')
    
    def mass_update_view(self, request):
        """Μαζική ενημέρωση πελατών"""
        if request.method == 'POST':
            action = request.POST.get('action')
            client_ids = request.POST.getlist('client_ids')
            
            clients = ClientProfile.objects.filter(id__in=client_ids)
            
            if action == 'activate':
                clients.update(is_active=True)
                messages.success(request, f'✅ Ενεργοποιήθηκαν {clients.count()} πελάτες')
            elif action == 'deactivate':
                clients.update(is_active=False)
                messages.warning(request, f'⚠️ Απενεργοποιήθηκαν {clients.count()} πελάτες')
            elif action == 'change_category':
                new_category = request.POST.get('new_category')
                clients.update(katigoria_vivlion=new_category)
                messages.success(request, f'✅ Αλλαγή κατηγορίας σε {clients.count()} πελάτες')
            elif action == 'change_type':
                new_type = request.POST.get('new_type')
                clients.update(eidos_ipoxreou=new_type)
                messages.success(request, f'✅ Αλλαγή τύπου σε {clients.count()} πελάτες')
            
            return redirect('..')
        
        context = {
            'title': 'Μαζική Ενημέρωση Πελατών',
            'clients': ClientProfile.objects.all(),
            'has_permission': True,
        }
        return render(request, 'admin/accounting/mass_update.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """Προσθήκη buttons στο changelist"""
        extra_context = extra_context or {}
        extra_context.update({
            'show_import_export': True,
        })
        return super().changelist_view(request, extra_context)


# ============================================================================
# ADMIN CLASSES - OBLIGATIONS
# ============================================================================
# ... (το υπόλοιπο του αρχείου μένει ίδιο)
# ============================================================================
# ADMIN CLASSES - OBLIGATIONS
# ============================================================================

@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'client', 'document_category', 'file_type', 'uploaded_at']
    list_filter = ['document_category', 'file_type', 'uploaded_at']
    search_fields = ['client__eponimia', 'client__afm', 'filename', 'description']
    raw_id_fields = ['client', 'obligation']


@admin.register(ArchiveConfiguration)
class ArchiveConfigurationAdmin(admin.ModelAdmin):
    list_display = ['obligation_type', 'filename_pattern', 'folder_pattern', 'create_subfolder']
    list_filter = ['create_subfolder', 'allow_multiple_files']
    search_fields = ['obligation_type__name', 'obligation_type__code']


@admin.register(ObligationGroup)
class ObligationGroupAdmin(admin.ModelAdmin):
    form = ObligationGroupForm
    list_display = ['name', 'description', 'get_obligations_count', 'get_obligations_list']
    search_fields = ['name']
    
    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields': ('name', 'description')
        }),
        ('Υποχρεώσεις Αλληλοαποκλεισμού', {
            'fields': ('obligation_types',),
            'description': '⚠️ Οι υποχρεώσεις σε αυτήν την ομάδα αλληλοαποκλείονται - ένας πελάτης μπορεί να έχει μόνο μία από αυτές.'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        ObligationType.objects.filter(exclusion_group=obj).update(exclusion_group=None)
        
        selected_types = form.cleaned_data.get('obligation_types', [])
        for obl_type in selected_types:
            obl_type.exclusion_group = obj
            obl_type.save()
        
        messages.success(request, f'✅ Ομάδα "{obj.name}" ενημερώθηκε με {len(selected_types)} υποχρεώσεις!')
    
    def get_obligations_count(self, obj):
        return obj.obligationtype_set.count()
    get_obligations_count.short_description = 'Πλήθος'
    
    def get_obligations_list(self, obj):
        obligations = obj.obligationtype_set.all()[:3]
        names = [o.name for o in obligations]
        if obj.obligationtype_set.count() > 3:
            names.append('...')
        return ', '.join(names) if names else '—'
    get_obligations_list.short_description = 'Υποχρεώσεις'


@admin.register(ObligationProfile)
class ObligationProfileAdmin(admin.ModelAdmin):
    form = ObligationProfileForm
    list_display = ['name', 'description', 'get_obligation_count', 'get_obligations_list']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields': ('name', 'description')
        }),
        ('Υποχρεώσεις Profile', {
            'fields': ('obligation_types',),
            'description': '💡 Όταν ένας πελάτης επιλέγει αυτό το profile, όλες οι παρακάτω υποχρεώσεις ενεργοποιούνται αυτόματα.'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        ObligationType.objects.filter(profile=obj).update(profile=None)
        
        selected_types = form.cleaned_data.get('obligation_types', [])
        for obl_type in selected_types:
            obl_type.profile = obj
            obl_type.save()
        
        messages.success(request, f'✅ Profile "{obj.name}" ενημερώθηκε με {len(selected_types)} υποχρεώσεις!')
    
    def get_obligation_count(self, obj):
        return obj.obligations.count()
    get_obligation_count.short_description = 'Πλήθος'
    
    def get_obligations_list(self, obj):
        obligations = obj.obligations.all()[:3]
        names = [o.name for o in obligations]
        if obj.obligations.count() > 3:
            names.append('...')
        return ', '.join(names) if names else '—'
    get_obligations_list.short_description = 'Υποχρεώσεις'


@admin.register(ObligationType)
class ObligationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'frequency', 'deadline_type', 'profile', 'exclusion_group', 'is_active', 'priority']
    list_filter = ['frequency', 'is_active', 'profile', 'exclusion_group']
    search_fields = ['name', 'code']
    list_editable = ['priority', 'is_active']
    
    fieldsets = (
        ('Βασικά', {
            'fields': ('name', 'code', 'description', 'is_active', 'priority')
        }),
        ('Χρονικά', {
            'fields': ('frequency', 'deadline_type', 'deadline_day', 'applicable_months')
        }),
        ('Σχέσεις', {
            'fields': ('exclusion_group', 'profile')
        }),
    )


@admin.register(ClientObligation)
class ClientObligationAdmin(admin.ModelAdmin):
    form = ClientObligationForm
    list_display = ['client', 'is_active', 'created_at']
    list_filter = ['is_active', 'obligation_profiles']
    search_fields = ['client__afm', 'client__eponimia']
    filter_horizontal = ['obligation_types', 'obligation_profiles']
    
    fieldsets = (
        ('Πελάτης', {
            'fields': ('client', 'is_active')
        }),
        ('Υποχρεώσεις', {
            'fields': ('obligation_profiles', 'obligation_types'),
            'description': '⚠️ Προσοχή: Δεν μπορείτε να επιλέξετε ΦΠΑ Μηνιαίο ΚΑΙ Τρίμηνο ταυτόχρονα!'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f'✅ Οι υποχρεώσεις του πελάτη {obj.client.eponimia} αποθηκεύτηκαν επιτυχώς!')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-assign/', self.admin_site.admin_view(self.bulk_assign_view), 
                 name='accounting_clientobligation_bulk'),
        ]
        return custom_urls + urls
    
    def bulk_assign_view(self, request):
        """Μαζική ανάθεση υποχρεώσεων"""
        if request.method == 'POST':
            form = BulkAssignForm(request.POST)
            if form.is_valid():
                clients = form.cleaned_data['clients']
                profiles = form.cleaned_data['obligation_profiles']
                types = form.cleaned_data['obligation_types']
                
                # Validate ΦΠΑ
                type_names = [t.name for t in types]
                has_monthly = any('ΦΠΑ Μηνιαίο' in name or 'ΦΠΑ ΜΗΝΙΑΙΟ' in name.upper() for name in type_names)
                has_quarterly = any('ΦΠΑ Τρίμηνο' in name or 'ΦΠΑ ΤΡΙΜΗΝΟ' in name.upper() for name in type_names)
                
                if has_monthly and has_quarterly:
                    messages.error(request, '❌ Δεν μπορείτε να επιλέξετε ταυτόχρονα ΦΠΑ Μηνιαίο και ΦΠΑ Τρίμηνο!')
                    return render(request, 'admin/accounting/bulk_assign.html', {
                        'form': form,
                        'title': 'Μαζική Ανάθεση Υποχρεώσεων',
                        'has_permission': True,
                        'media': self.media + form.media,
                    })
                
                created_count = 0
                updated_count = 0
                
                for client in clients:
                    client_obl, created = ClientObligation.objects.get_or_create(
                        client=client,
                        defaults={'is_active': True}
                    )
                    
                    for profile in profiles:
                        client_obl.obligation_profiles.add(profile)
                    
                    for obl_type in types:
                        client_obl.obligation_types.add(obl_type)
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                messages.success(
                    request,
                    f'✅ Ανατέθηκαν υποχρεώσεις σε {len(clients)} πελάτες! '
                    f'(Νέοι: {created_count}, Ενημερωμένοι: {updated_count})'
                )
                return redirect('..')
        else:
            form = BulkAssignForm()
        
        context = {
            'form': form,
            'title': 'Μαζική Ανάθεση Υποχρεώσεων',
            'has_permission': True,
            'media': self.media + form.media,
        }
        
        return render(request, 'admin/accounting/bulk_assign.html', context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_bulk_assign'] = True
        return super().changelist_view(request, extra_context)


# ============================================================================
# INLINES - Document management
# ============================================================================

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


@admin.register(MonthlyObligation)
class MonthlyObligationAdmin(admin.ModelAdmin):
    # ✅ INLINE DOCUMENTS - Detail view με συνημμένα
    inlines = [ClientDocumentInline]

    list_display = [
        'client_display',  # ✅ Νέο με link
        'obligation_type',
        'deadline_with_icon',
        'status_badge',  # Enhanced
        'time_spent',
        'cost_display',
        'has_attachment',
        'completed_by_display',  # Enhanced
    ]

    # ✅ AUTOCOMPLETE ΓΙΑ CLIENT
    autocomplete_fields = ['client', 'obligation_type']
    
    # ✅ ENHANCED ΦΙΛΤΡΑ
    list_filter = [
        'status',
        'year',
        'month',
        'obligation_type',
        'completed_by',
        ('deadline', admin.DateFieldListFilter),
        ('client__eidos_ipoxreou', admin.ChoicesFieldListFilter),  # ✅ Νέο!
        ('client__is_active', admin.BooleanFieldListFilter),  # ✅ Νέο!
        ('client__katigoria_vivlion', admin.ChoicesFieldListFilter),  # ✅ Bonus!
    ]
    
    # ✅ ENHANCED SEARCH
    search_fields = [
        'client__afm',
        'client__eponimia',
        'client__onoma',
        'client__email',
        'client__kinito_tilefono',
        'client__tilefono_epixeirisis_1',
        'obligation_type__name',
        'obligation_type__code',
        'notes'
    ]
    
    list_editable = ['time_spent']
    readonly_fields = [
        'created_at',
        'updated_at',
        'completed_by',
        'completed_date',
        'calculated_cost',
        'current_attachment'
    ]
    date_hierarchy = 'deadline'
    list_per_page = 50
    actions = ['mark_as_completed', 'mark_as_pending', 'export_obligations_csv']
    
    fieldsets = (
        ('Βασικά', {
            'fields': ('client', 'obligation_type', 'year', 'month', 'deadline')
        }),
        ('Κατάσταση', {
            'fields': ('status', 'completed_date', 'completed_by')
        }),
        ('Χρέωση', {
            'fields': ('time_spent', 'hourly_rate', 'calculated_cost'),
        }),
        ('Σημειώσεις & Αρχεία', {
            'fields': ('notes', 'current_attachment', 'attachment'),
        }),
    )
    
    # ============================================
    # ✅ DISPLAY METHODS - ENHANCED
    # ============================================
    
    def client_display(self, obj):
        """Πελάτης με link και επιπλέον πληροφορίες"""
        url = reverse('admin:accounting_clientprofile_change', args=[obj.client.id])

        # Badge για active/inactive
        active_badge = ''
        if not obj.client.is_active:
            active_badge = '<span style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; margin-left: 5px;">ΑΝΕΝΕΡΓΟΣ</span>'

        # ✅ SECURITY FIX: Explicitly escape user input to prevent XSS
        return format_html(
            '<a href="{}" style="font-weight: 600; color: #667eea; text-decoration: none;">'
            '👤 {}'
            '</a>{}<br>'
            '<small style="color: #666;">ΑΦΜ: {} • {}</small>',
            url,
            escape(obj.client.eponimia),
            active_badge,
            escape(obj.client.afm),
            escape(obj.client.get_eidos_ipoxreou_display())
        )
    client_display.short_description = '👤 Πελάτης'
    client_display.admin_order_field = 'client__eponimia'
    
    def status_badge(self, obj):
        """Status με έγχρωμο badge"""
        colors = {
            'pending': ('#f59e0b', '⏳', 'Εκκρεμεί'),
            'completed': ('#10b981', '✅', 'Ολοκληρώθηκε'),
            'overdue': ('#ef4444', '🔴', 'Καθυστερεί'),
        }
        color, icon, label = colors.get(obj.status, ('#666', '?', obj.status))
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85em;">{} {}</span>',
            color, icon, label
        )
    status_badge.short_description = 'Κατάσταση'
    status_badge.admin_order_field = 'status'
    
    def completed_by_display(self, obj):
        """Completed by με avatar-style"""
        if obj.completed_by:
            initials = ''.join([word[0].upper() for word in obj.completed_by.get_full_name().split()[:2]]) if obj.completed_by.get_full_name() else obj.completed_by.username[0].upper()
            return format_html(
                '<div style="display: inline-flex; align-items: center;">'
                '<span style="background: #667eea; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.75em; margin-right: 6px;">{}</span>'
                '<span style="font-size: 0.9em;">{}</span>'
                '</div>',
                initials,
                obj.completed_by.get_full_name() or obj.completed_by.username
            )
        return '—'
    completed_by_display.short_description = '✓ Από'
    completed_by_display.admin_order_field = 'completed_by'
    
    def current_attachment(self, obj):
        """Display current attachment"""
        if obj.attachment:
            filename = os.path.basename(obj.attachment.name)
            try:
                file_size = round(obj.attachment.size / 1024, 1)
            except:
                file_size = '—'

            # ✅ SECURITY FIX: Escape filename to prevent XSS
            return format_html(
                '<div style="padding: 10px; background: #f0f8ff; border-radius: 6px; border-left: 4px solid #667eea;">'
                '<strong>📎 Τρέχον Αρχείο:</strong><br>'
                '<a href="{}" target="_blank" style="color: #667eea; font-weight: 600; text-decoration: none;">{}</a>'
                '<div style="font-size: 12px; color: #666; margin-top: 5px;">Μέγεθος: {} KB</div>'
                '</div>',
                obj.attachment.url,
                escape(filename),
                file_size
            )
        return "—"
    current_attachment.short_description = 'Συνημμένο'
    
    def calculated_cost(self, obj):
        """Show calculated cost"""
        try:
            if obj.cost:
                cost_value = float(obj.cost)
                return format_html(
                    '<span style="font-weight: 600; color: #059669;">€{:.2f}</span>',
                    cost_value
                )
        except (TypeError, ValueError, AttributeError):
            pass
        return "—"
    calculated_cost.short_description = 'Υπολογισμένο Κόστος'   
    
    def cost_display(self, obj):
        """For list display"""
        try:
            if obj.cost:
                # Βεβαιώσου ότι είναι float
                cost_value = float(obj.cost)
                return format_html(
                    '<span style="font-weight: 600; color: #059669;">€{:.2f}</span>',
                    cost_value
                )
        except (TypeError, ValueError, AttributeError):
            pass
        return "—"
    cost_display.short_description = 'Κόστος'
    cost_display.admin_order_field = 'time_spent'    
    
    def has_attachment(self, obj):
        """Show attachment indicator in list"""
        if obj.attachment:
            return format_html('<span style="font-size: 1.2em;">📎</span>')
        return format_html('<span style="color: #ccc;">—</span>')
    has_attachment.short_description = 'Αρχείο'
    
    def deadline_with_icon(self, obj):
        """Deadline με χρωματιστό icon και countdown"""
        if obj.status == 'completed':
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">✅ {}</span><br>'
                '<small style="color: #666;">Ολοκληρώθηκε {}</small>',
                obj.deadline.strftime('%d/%m/%Y'),
                obj.completed_date.strftime('%d/%m/%Y') if obj.completed_date else ''
            )
        
        days = obj.days_until_deadline
        if days < 0:
            icon = '🔴'
            color = '#dc3545'
            text = f'Καθυστερεί {abs(days)} ημέρες'
            urgency = 'ΕΠΕΙΓΟΝ!'
        elif days == 0:
            icon = '⚠️'
            color = '#ffc107'
            text = 'Λήγει ΣΗΜΕΡΑ'
            urgency = 'ΣΗΜΕΡΑ!'
        elif days <= 3:
            icon = '🟡'
            color = '#ffc107'
            text = f'Απομένουν {days} ημέρες'
            urgency = 'Προσοχή'
        else:
            icon = '🟢'
            color = '#28a745'
            text = f'Απομένουν {days} ημέρες'
            urgency = ''
        
        return format_html(
            '{} <span style="color: {}; font-weight: 600;">{}</span><br>'
            '<small style="color: {}; font-weight: 600;">{}</small>'
            '{}',
            icon,
            color,
            obj.deadline.strftime('%d/%m/%Y'),
            color,
            text,
            f'<br><small style="background: {color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; font-weight: 600;">{urgency}</small>' if urgency else ''
        )
    deadline_with_icon.short_description = '📅 Προθεσμία'
    deadline_with_icon.admin_order_field = 'deadline'
    
    # ============================================
    # ACTIONS - SAME AS BEFORE
    # ============================================
    
    @admin.action(description='✓ Ολοκλήρωση επιλεγμένων')
    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'overdue']).update(
            status='completed',
            completed_date=timezone.now().date(),
            completed_by=request.user
        )
        self.message_user(request, f'✅ Ολοκληρώθηκαν {updated} υποχρεώσεις!', messages.SUCCESS)
    
    @admin.action(description='↺ Επαναφορά σε εκκρεμεί')
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(
            status='pending',
            completed_date=None,
            completed_by=None
        )
        self.message_user(request, f'↺ Επαναφέρθηκαν {updated} υποχρεώσεις!', messages.SUCCESS)
    
    @admin.action(description='📊 Export σε CSV')
    def export_obligations_csv(self, request, queryset):
        """Export obligations to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="obligations_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Πελάτης',
            'ΑΦΜ',
            'Είδος Υπόχρεου',
            'Ενεργός',
            'Υποχρέωση',
            'Κωδικός',
            'Μήνας',
            'Έτος',
            'Προθεσμία',
            'Κατάσταση',
            'Χρόνος (ώρες)',
            'Ωριαία Χρέωση (€)',
            'Κόστος (€)',
            'Ολοκληρώθηκε',
            'Από'
        ])
        
        for obl in queryset.select_related('client', 'obligation_type', 'completed_by'):
            writer.writerow([
                obl.client.eponimia,
                obl.client.afm,
                obl.client.get_eidos_ipoxreou_display(),
                'Ναι' if obl.client.is_active else 'Όχι',
                obl.obligation_type.name,
                obl.obligation_type.code,
                obl.month,
                obl.year,
                obl.deadline.strftime('%d/%m/%Y'),
                obl.get_status_display(),
                obl.time_spent or '',
                obl.hourly_rate or '',
                f"{obl.cost:.2f}" if obl.cost else '',
                obl.completed_date.strftime('%d/%m/%Y') if obl.completed_date else '',
                obl.completed_by.get_full_name() if obl.completed_by else ''
            ])
        
        self.message_user(request, f'✅ Εξήχθησαν {queryset.count()} υποχρεώσεις', messages.SUCCESS)
        return response
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'completed' and not obj.completed_by:
            obj.completed_by = request.user
            obj.completed_date = timezone.now().date()
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate/', self.admin_site.admin_view(self.generate_obligations_view), 
                 name='accounting_monthlyobligation_generate'),
        ]
        return custom_urls + urls
    
    def generate_obligations_view(self, request):
        """Custom view για δημιουργία μηνιαίων υποχρεώσεων"""
        if request.method == 'POST':
            form = GenerateObligationsForm(request.POST)
            if form.is_valid():
                year = form.cleaned_data['year']
                month = form.cleaned_data['month']
                
                created_count = 0
                skipped_count = 0
                
                client_obligations = ClientObligation.objects.filter(is_active=True)
                
                for client_obl in client_obligations:
                    client = client_obl.client
                    obligation_types = client_obl.get_all_obligation_types()
                    
                    for obligation_type in obligation_types:
                        if not obligation_type.applies_to_month(month):
                            continue
                        
                        deadline = obligation_type.get_deadline_for_month(year, month)
                        
                        if not deadline:
                            continue
                        
                        monthly_obl, created = MonthlyObligation.objects.get_or_create(
                            client=client,
                            obligation_type=obligation_type,
                            year=year,
                            month=month,
                            defaults={
                                'deadline': deadline,
                                'status': 'pending'
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1
                
                messages.success(
                    request,
                    f'✅ Δημιουργήθηκαν {created_count} νέες υποχρεώσεις για {month}/{year}. '
                    f'({skipped_count} υπήρχαν ήδη)'
                )
                return redirect('..')
        else:
            form = GenerateObligationsForm()
        
        context = {
            'form': form,
            'title': 'Δημιουργία Μηνιαίων Υποχρεώσεων',
            'has_permission': True,
        }
        
        return render(request, 'admin/accounting/generate_obligations.html', context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generate_button'] = True
        return super().changelist_view(request, extra_context)
    
    # ============================================
    # ✅ OPTIMIZE QUERYSET
    # ============================================
    
    def get_queryset(self, request):
        """Optimize queries με select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('client', 'obligation_type', 'completed_by')

# ============================================================================
# EMAIL AUTOMATION
# ============================================================================

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_active', 'created_at', 'preview_button']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subject', 'body_html']
    
    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'body_html'),
            'description': '''
            <strong>Διαθέσιμες Μεταβλητές:</strong><br>
            • <code>{{client.eponimia}}</code> - Επωνυμία πελάτη<br>
            • <code>{{client.afm}}</code> - ΑΦΜ<br>
            • <code>{{client.email}}</code> - Email<br>
            • <code>{{obligation.name}}</code> - Όνομα υποχρέωσης<br>
            • <code>{{obligation.deadline}}</code> - Προθεσμία<br>
            • <code>{{user.name}}</code> - Το όνομά σας<br>
            • <code>{{company_name}}</code> - Όνομα εταιρείας<br>
            • <code>{{completed_date}}</code> - Ημερομηνία ολοκλήρωσης
            '''
        }),
    )
    
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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        status = "ενημερώθηκε" if change else "δημιουργήθηκε"
        messages.success(request, f'✅ Ο κανόνας "{obj.name}" {status} επιτυχώς!')


@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = [
        'recipient_name',
        'subject_preview',
        'send_at',
        'status',
        'obligations_count',
        'actions_column'
    ]
    list_filter = ['status', 'send_at', 'created_at']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
    filter_horizontal = ['obligations']
    readonly_fields = ['sent_at', 'error_message', 'created_by', 'created_at']
    
    fieldsets = (
        ('Παραλήπτης', {
            'fields': ('recipient_name', 'recipient_email', 'client')
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
    
    def subject_preview(self, obj):
        # ✅ SECURITY FIX: Escape subject to prevent XSS
        preview = escape(obj.subject[:50])
        if len(obj.subject) > 50:
            preview += '...'
        return preview
    subject_preview.short_description = 'Θέμα'
    
    def obligations_count(self, obj):
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


# ============================================================================
# VOIP & TICKETS
# ============================================================================

@admin.register(VoIPCall)
class VoIPCallAdmin(admin.ModelAdmin):
    """Complete VoIP Admin"""
    
    list_display = [
        'call_id_colored',
        'phone_number_link',
        'client_link',
        'direction_icon',
        'status_badge',
        'resolution_badge',       
        'duration_display',
        'started_at_formatted',
        'ticket_badge',
    ]
    
    list_filter = [
        'status',
        'direction',
        'resolution',  
        'started_at',
        'ticket_created',
        ('client', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = ['phone_number', 'client__eponimia', 'client_email', 'call_id', 'notes']
    readonly_fields = ['call_id', 'duration_formatted', 'created_at', 'updated_at', 'logs_display']
    
    actions = [
        'mark_as_closed',
        'mark_as_follow_up',
        'mark_as_pending',
        'export_calls_csv',
    ]
    
    fieldsets = (
        ('📞 Κλήση - Βασικά', {
            'fields': ('call_id', 'phone_number', 'direction', 'status'),
        }),
        ('👤 Πελάτης', {
            'fields': ('client', 'client_email'),
        }),
        ('⏱️ Χρονισμός', {
            'fields': ('started_at', 'ended_at', 'duration_seconds', 'duration_formatted'),
        }),
        ('📝 Σημειώσεις & Ευστάθεια', {
            'fields': ('notes', 'resolution'),
        }),
        ('🎫 Τίκετ', {
            'fields': ('ticket_created', 'ticket_id'),
        }),
        ('📊 Ιστορικό', {
            'fields': ('logs_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-started_at']
    date_hierarchy = 'started_at'
    list_per_page = 50
    
    # Display methods
    def call_id_colored(self, obj):
        return format_html(
            '<span style="background-color: #e3f2fd; padding: 6px 12px; border-radius: 4px; font-family: monospace; font-weight: 600;">{}</span>',
            obj.call_id
        )
    call_id_colored.short_description = '📱 Call ID'
    
    def phone_number_link(self, obj):
        # ✅ SECURITY FIX: Escape phone number to prevent XSS
        return format_html(
            '<a href="tel:{}" style="color: #2563eb; text-decoration: none; font-weight: 600;">📞 {}</a>',
            escape(obj.phone_number),
            escape(obj.phone_number)
        )
    phone_number_link.short_description = '🔔 Αριθμός'

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounting_clientprofile_change', args=[obj.client.id])
            # ✅ SECURITY FIX: Escape client name to prevent XSS
            return format_html(
                '<a href="{}" style="color: #059669; font-weight: 600;">👤 {}</a>',
                url,
                escape(obj.client.eponimia)
            )
        return format_html('<span style="color: #999;">—</span>')
    client_link.short_description = '👤 Πελάτης'
    
    def direction_icon(self, obj):
        if obj.direction == 'incoming':
            return format_html('<span style="font-size: 1.2em;">📲</span> Εισερχόμενη')
        return format_html('<span style="font-size: 1.2em;">☎️</span> Εξερχόμενη')
    direction_icon.short_description = 'Κατεύθυνση'
    
    def status_badge(self, obj):
        colors = {
            'missed': ('#dc2626', '❌', 'Αναπάντητη'),
            'completed': ('#16a34a', '✅', 'Ολοκληρώθηκε'),
            'active': ('#2563eb', '🔵', 'Ενεργή'),
            'failed': ('#ea580c', '⚠️', 'Αποτυχία'),
        }
        color, icon, label = colors.get(obj.status, ('#999', '❓', obj.status))
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600;">{} {}</span>',
            color, icon, label
        )
    status_badge.short_description = 'Κατάσταση'
    
    def resolution_badge(self, obj):
        if not obj.resolution:
            return format_html('<span style="color: #999;">—</span>')
        
        colors = {
            'pending': ('#f59e0b', '⏳', 'Εκρεμμότητα'),
            'closed': ('#10b981', '✅', 'Κλειστή'),
            'follow_up': ('#3b82f6', '📞', 'Follow-up'),
        }
        color, icon, label = colors.get(obj.resolution, ('#999', '?', obj.resolution))
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600;">{} {}</span>',
            color, icon, label
        )
    resolution_badge.short_description = 'Ευστάθεια'
    
    def duration_display(self, obj):
        return format_html(
            '<span style="background: #f3f4f6; padding: 6px 12px; border-radius: 4px; font-weight: 600;">⏱️ {}</span>',
            obj.duration_formatted
        )
    duration_display.short_description = 'Διάρκεια'
    
    def started_at_formatted(self, obj):
        return obj.started_at.strftime('%d/%m/%Y\n%H:%M:%S')
    started_at_formatted.short_description = '📅 Ημερ/Ώρα'
    
    def ticket_badge(self, obj):
        if obj.ticket_created:
            return format_html(
                '<span style="background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 4px; font-weight: 600;">🎫 ΝΑΙ</span>'
            )
        return format_html(
            '<span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-weight: 600;">✗ ΌΧΙ</span>'
        )
    ticket_badge.short_description = 'Τίκετ'
    
    def logs_display(self, obj):
        logs = obj.logs.all().order_by('-created_at')[:10]
        html = '<div style="max-height: 300px; overflow-y: auto;">'
        for log in logs:
            html += f'<div style="border-left: 3px solid #2563eb; padding: 8px; margin: 5px 0;"><strong>{log.get_action_display()}</strong><br><small style="color: #666;">{log.created_at.strftime("%d/%m %H:%M")} - {log.description}</small></div>'
        html += '</div>'
        return format_html(html)
    logs_display.short_description = 'Ιστορικό'
    
    # Actions
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(resolution='closed')
        self.message_user(request, f'✅ {updated} κλήσεις σημειώθηκαν ως κλειστές!')
        logger.info(f"{request.user} marked {updated} calls as closed")
    mark_as_closed.short_description = '✅ Κλείσιμο'
    
    def mark_as_follow_up(self, request, queryset):
        updated = queryset.update(resolution='follow_up')
        self.message_user(request, f'📞 {updated} κλήσεις χρειάζονται follow-up!')
        logger.info(f"{request.user} marked {updated} calls as follow_up")
    mark_as_follow_up.short_description = '📞 Follow-up'
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(resolution='pending')
        self.message_user(request, f'⏳ {updated} κλήσεις σημειώθηκαν ως εκρεμμότητες!')
        logger.info(f"{request.user} marked {updated} calls as pending")
    mark_as_pending.short_description = '⏳ Εκκρεμεί'
    
    def export_calls_csv(self, request, queryset):
        """Export to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="calls_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Αριθμός', 'Πελάτης', 'Κατεύθυνση', 'Κατάσταση', 'Ευστάθεια', 'Διάρκεια', 'Ημερομηνία'])
        
        for call in queryset:
            writer.writerow([
                call.phone_number,
                call.client.eponimia if call.client else '—',
                call.get_direction_display(),
                call.get_status_display(),
                call.get_resolution_display() if call.resolution else '—',
                call.duration_formatted,
                call.started_at.strftime('%d/%m/%Y %H:%M'),
            ])
        
        logger.info(f"{request.user} exported {queryset.count()} calls to CSV")
        return response
    export_calls_csv.short_description = '📊 Export CSV'


@admin.register(VoIPCallLog)
class VoIPCallLogAdmin(admin.ModelAdmin):
    """VoIP Call Logs - Audit Trail"""
    
    list_display = ['call_link', 'action_badge', 'description_short', 'created_at_formatted']
    list_filter = ['action', 'created_at']
    search_fields = ['call__phone_number', 'description']
    readonly_fields = ['call', 'action', 'description', 'created_at']
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def call_link(self, obj):
        url = reverse('admin:accounting_voipcall_change', args=[obj.call.id])
        # ✅ SECURITY FIX: Escape phone number to prevent XSS
        return format_html(
            '<a href="{}" style="color: #2563eb; font-weight: 600;">📞 {}</a>',
            url,
            escape(obj.call.phone_number)
        )
    call_link.short_description = 'Κλήση'
    
    def action_badge(self, obj):
        colors = {
            'started': '#3b82f6',
            'ended': '#10b981',
            'ticket_created': '#f59e0b',
            'client_matched': '#8b5cf6',
            'status_changed': '#06b6d4',
        }
        color = colors.get(obj.action, '#666')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 600;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Ενέργεια'
    
    def description_short(self, obj):
        # ✅ SECURITY FIX: Escape description to prevent XSS
        desc = escape(obj.description)
        return desc[:80] + '...' if len(obj.description) > 80 else desc
    description_short.short_description = 'Περιγραφή'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M:%S')
    created_at_formatted.short_description = 'Χρόνος'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Professional Ticket Admin"""
    
    list_display = [
        'ticket_id_display',
        'title_short',
        'client_link',
        'call_link',
        'status_badge',
        'priority_badge',
        'assigned_to_display',
        'created_at_formatted',
        'days_open'
    ]
    
    list_filter = [
        'status',
        'priority',
        'created_at',
        'assigned_to',
        ('client', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'title',
        'description',
        'call__phone_number',
        'client__eponimia',
        'notes'
    ]
    
    readonly_fields = [
        'created_at',
        'assigned_at',
        'resolved_at',
        'closed_at',
        'call_info',
    ]
    
    fieldsets = (
        ('🎫 Ticket Info', {
            'fields': ('call', 'call_info', 'title', 'description')
        }),
        ('👤 Client & Assignment', {
            'fields': ('client', 'assigned_to')
        }),
        ('📊 Status', {
            'fields': ('status', 'priority')
        }),
        ('📝 Notes', {
            'fields': ('notes',)
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'assigned_at', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('🔔 Notifications', {
            'fields': ('email_sent', 'follow_up_scheduled')
        }),
    )
    
    actions = [
        'mark_as_assigned',
        'mark_as_in_progress',
        'mark_as_resolved',
        'mark_as_closed',
        'export_tickets_csv',
    ]
    
    ordering = ['-created_at']
    
    # Display methods
    def ticket_id_display(self, obj):
        return format_html(
            '<span style="background: #667eea; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">#{}</span>',
            obj.id
        )
    ticket_id_display.short_description = '🎫'
    
    def title_short(self, obj):
        # ✅ SECURITY FIX: Escape title to prevent XSS
        title = escape(obj.title)
        return title[:50] + '...' if len(obj.title) > 50 else title
    title_short.short_description = 'Τίτλος'

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounting_clientprofile_change', args=[obj.client.id])
            # ✅ SECURITY FIX: Escape client name to prevent XSS
            return format_html('<a href="{}">{}</a>', url, escape(obj.client.eponimia))
        return '—'
    client_link.short_description = 'Πελάτης'
    
    def call_link(self, obj):
        if obj.call:
            url = reverse('admin:accounting_voipcall_change', args=[obj.call.id])
            return format_html('<a href="{}">{}</a>', url, f'Call #{obj.call.id}')
        return '—'
    call_link.short_description = 'Κλήση'
    
    def call_info(self, obj):
        if obj.call:
            # ✅ SECURITY FIX: Escape phone number to prevent XSS
            return format_html(
                '📞 {}<br>↔️ {}<br>🕐 {}<br>⏱️ {}',
                escape(obj.call.phone_number),
                escape(obj.call.get_direction_display()),
                obj.call.started_at.strftime('%d/%m/%Y %H:%M'),
                escape(obj.call.duration_formatted)
            )
        return '—'
    call_info.short_description = 'Call Details'
    
    def status_badge(self, obj):
        colors = {
            'open': '#ef4444',
            'assigned': '#f59e0b',
            'in_progress': '#3b82f6',
            'resolved': '#10b981',
            'closed': '#6b7280',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Κατάσταση'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#10b981',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'urgent': '#991b1b',
        }
        color = colors.get(obj.priority, '#666')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Προτεραιότητα'
    
    def assigned_to_display(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return '—'
    assigned_to_display.short_description = 'Ανατεθειμένο'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = 'Δημιουργήθηκε'
    
    def days_open(self, obj):
        days = obj.days_since_created
        if days == 0:
            color = '#10b981'
            text = 'Σήμερα'
        elif days <= 3:
            color = '#f59e0b'
            text = f'{days} ημέρες'
        else:
            color = '#ef4444'
            text = f'{days} ημέρες'
        
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, text
        )
    days_open.short_description = 'Διάρκεια'
    
    # Actions
    def mark_as_assigned(self, request, queryset):
        updated = queryset.update(status='assigned')
        self.message_user(request, f'✅ {updated} tickets marked as assigned')
    mark_as_assigned.short_description = '✅ Assigned'
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'⏳ {updated} tickets marked as in progress')
    mark_as_in_progress.short_description = '⏳ In Progress'
    
    def mark_as_resolved(self, request, queryset):
        updated = 0
        for ticket in queryset:
            ticket.mark_as_resolved()
            updated += 1
        self.message_user(request, f'✅ {updated} tickets resolved')
    mark_as_resolved.short_description = '✅ Resolved'
    
    def mark_as_closed(self, request, queryset):
        updated = 0
        for ticket in queryset:
            ticket.mark_as_closed()
            updated += 1
        self.message_user(request, f'🔒 {updated} tickets closed')
    mark_as_closed.short_description = '🔒 Closed'
    
    def export_tickets_csv(self, request, queryset):
        """Export to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="tickets_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Τίτλος', 'Πελάτης', 'Κατάσταση', 'Προτεραιότητα', 'Ανατεθειμένο', 'Δημιουργήθηκε', 'Ημέρες Ανοιχτό'])
        
        for ticket in queryset:
            writer.writerow([
                ticket.id,
                ticket.title,
                ticket.client.eponimia if ticket.client else '—',
                ticket.get_status_display(),
                ticket.get_priority_display(),
                ticket.assigned_to.get_full_name() if ticket.assigned_to else '—',
                ticket.created_at.strftime('%d/%m/%Y %H:%M'),
                ticket.days_since_created
            ])
        
        self.message_user(request, f'✅ Εξήχθησαν {queryset.count()} tickets')
        return response
    export_tickets_csv.short_description = '📊 Export CSV'
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.assigned_to:
            obj.assigned_to = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# CUSTOM ADMIN INDEX
# ============================================================================

admin.site.index_template = 'admin/custom_index.html'
admin.site.site_header = 'LogistikoCRM Administration'
admin.site.site_title = 'LogistikoCRM'
admin.site.index_title = 'Καλώς ήρθατε στο LogistikoCRM'
