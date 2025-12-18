from django.db import models
from django.contrib.auth.models import User
from crm.models import Company, Contact
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os
import re
from django.conf import settings
from django.utils.text import slugify


class ClientProfile(models.Model):
    """Επέκταση στοιχείων πελάτη για λογιστικό"""
    
    TAXPAYER_TYPE_CHOICES = [
        ('individual', 'Ιδιώτης'),
        ('professional', 'Επαγγελματίας'),
        ('company', 'Εταιρεία'),
    ]
    
    BOOK_CATEGORY_CHOICES = [
        ('A', 'Α Κατηγορία'),
        ('B', 'Β Κατηγορία'),
        ('C', 'Γ Κατηγορία'),
        ('none', 'Χωρίς Βιβλία'),
    ]
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='accounting_profile')
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='accounting_profile')
    
    afm = models.CharField('Α.Φ.Μ.', max_length=20, unique=True)
    doy = models.CharField('Δ.Ο.Υ.', max_length=100, blank=True, null=True, default='')
    eponimia = models.CharField('Επωνυμία/Επώνυμο', max_length=200)
    onoma = models.CharField('Όνομα', max_length=100, blank=True, null=True, default='')
    onoma_patros = models.CharField('Όνομα Πατρός', max_length=100, blank=True, null=True, default='')
    
    arithmos_taftotitas = models.CharField('Αριθμός Ταυτότητας', max_length=50, blank=True, null=True, default='')
    eidos_taftotitas = models.CharField('Είδος Ταυτότητας', max_length=50, blank=True, null=True, default='')
    prosopikos_arithmos = models.CharField('Προσωπικός Αριθμός', max_length=50, blank=True, null=True, default='')
    amka = models.CharField('Α.Μ.Κ.Α.', max_length=20, blank=True, null=True, default='')
    am_ika = models.CharField('Α.Μ. Ι.Κ.Α.', max_length=50, blank=True, null=True, default='')
    arithmos_gemi = models.CharField('Αριθμός Γ.Ε.ΜΗ.', max_length=50, blank=True, null=True, default='')
    arithmos_dypa = models.CharField('Αριθμός Δ.ΥΠ.Α', max_length=50, blank=True, null=True, default='')
    
    imerominia_gennisis = models.DateField('Ημ. Γέννησης', null=True, blank=True)
    imerominia_gamou = models.DateField('Ημ. Γάμου', null=True, blank=True)
    filo = models.CharField('Φύλο', max_length=10, choices=[('M', 'Άνδρας'), ('F', 'Γυναίκα')], blank=True, null=True, default='')
    
    diefthinsi_katoikias = models.CharField('Διεύθυνση Κατοικίας', max_length=200, blank=True, null=True, default='')
    arithmos_katoikias = models.CharField('Αριθμός', max_length=20, blank=True, null=True, default='')
    poli_katoikias = models.CharField('Πόλη Κατοικίας', max_length=100, blank=True, null=True, default='')
    dimos_katoikias = models.CharField('Δήμος Κατοικίας', max_length=100, blank=True, null=True, default='')
    nomos_katoikias = models.CharField('Νομός Κατοικίας', max_length=100, blank=True, null=True, default='')
    tk_katoikias = models.CharField('T.K. Κατοικίας', max_length=10, blank=True, null=True, default='')
    tilefono_oikias_1 = models.CharField('Τηλέφωνο Οικίας 1', max_length=20, blank=True, null=True, default='')
    tilefono_oikias_2 = models.CharField('Τηλέφωνο Οικίας 2', max_length=20, blank=True, null=True, default='')
    kinito_tilefono = models.CharField('Κινητό τηλέφωνο', max_length=20, blank=True, null=True, default='')
    
    diefthinsi_epixeirisis = models.CharField('Διεύθυνση Επιχείρησης', max_length=200, blank=True, null=True, default='')
    arithmos_epixeirisis = models.CharField('Αριθμός Επιχείρησης', max_length=20, blank=True, null=True, default='')
    poli_epixeirisis = models.CharField('Πόλη Επιχείρησης', max_length=100, blank=True, null=True, default='')
    dimos_epixeirisis = models.CharField('Δήμος Επιχείρησης', max_length=100, blank=True, null=True, default='')
    nomos_epixeirisis = models.CharField('Νομός Επιχείρησης', max_length=100, blank=True, null=True, default='')
    tk_epixeirisis = models.CharField('Τ.Κ. Επιχείρησης', max_length=10, blank=True, null=True, default='')
    tilefono_epixeirisis_1 = models.CharField('Τηλέφωνο Επιχείρησης 1', max_length=20, blank=True, null=True, default='')
    tilefono_epixeirisis_2 = models.CharField('Τηλέφωνο Επιχείρησης 2', max_length=20, blank=True, null=True, default='')
    email = models.EmailField('Email', blank=True, null=True, default='')
    
    trapeza = models.CharField('Τράπεζα', max_length=100, blank=True, null=True, default='')
    iban = models.CharField('IBAN', max_length=34, blank=True, null=True, default='')
    
    eidos_ipoxreou = models.CharField('Είδος Υπόχρεου', max_length=20, choices=TAXPAYER_TYPE_CHOICES, default='professional')
    katigoria_vivlion = models.CharField('Κατηγορία Βιβλίων', max_length=10, choices=BOOK_CATEGORY_CHOICES, blank=True, null=True, default='')
    nomiki_morfi = models.CharField('Νομική Μορφή', max_length=100, blank=True, null=True, default='')
    agrotis = models.BooleanField('Αγρότης', default=False)
    imerominia_enarksis = models.DateField('Ημ/νία Έναρξης Εργασιών', null=True, blank=True)
    
    onoma_xristi_taxisnet = models.CharField('Όνομα Χρήστη Taxis Net', max_length=100, blank=True, null=True, default='')
    kodikos_taxisnet = models.CharField('Κωδικός Taxis Net', max_length=100, blank=True, null=True, default='')
    onoma_xristi_ika_ergodoti = models.CharField('Όνομα Χρήστη Ι.Κ.Α. Εργοδότη', max_length=100, blank=True, null=True, default='')
    kodikos_ika_ergodoti = models.CharField('Κωδικός Ι.Κ.Α. Εργοδότη', max_length=100, blank=True, null=True, default='')
    onoma_xristi_gemi = models.CharField('Όνομα Χρήστη Γ.Ε.ΜΗ.', max_length=100, blank=True, null=True, default='')
    kodikos_gemi = models.CharField('Κωδικός Γ.Ε.ΜΗ.', max_length=100, blank=True, null=True, default='')
    
    afm_sizigou = models.CharField('Α.Φ.Μ Συζύγου', max_length=20, blank=True, null=True, default='')
    afm_foreas = models.CharField('Α.Φ.Μ. Φορέας', max_length=20, blank=True, null=True, default='')
    am_klidi = models.CharField('ΑΜ ΚΛΕΙΔΙ', max_length=50, blank=True, null=True, default='')

    # PERFORMANCE: Add index for frequently filtered fields
    is_active = models.BooleanField('Ενεργός', default=True, db_index=True)
    created_at = models.DateTimeField('Δημιουργήθηκε', auto_now_add=True)
    updated_at = models.DateTimeField('Ενημερώθηκε', auto_now=True)

    class Meta:
        verbose_name = 'Προφίλ Πελάτη'
        verbose_name_plural = 'Προφίλ Πελατών'
        
    def __str__(self):
        return f"{self.afm} - {self.eponimia}"


class ObligationGroup(models.Model):
    """Ομάδα αλληλοαποκλειόμενων υποχρεώσεων"""
    name = models.CharField('Όνομα Ομάδας', max_length=100, unique=True)
    description = models.TextField('Περιγραφή', blank=True)
    
    class Meta:
        verbose_name = 'Ομάδα Υποχρεώσεων'
        verbose_name_plural = 'Ομάδες Υποχρεώσεων'
        
    def __str__(self):
        return self.name


class ObligationProfile(models.Model):
    """Profile υποχρεώσεων που ενεργοποιούνται μαζί (π.χ. Μισθοδοσία)"""
    name = models.CharField('Όνομα Profile', max_length=100, unique=True)
    description = models.TextField('Περιγραφή', blank=True)
    
    class Meta:
        verbose_name = 'Profile Υποχρεώσεων'
        verbose_name_plural = 'Profiles Υποχρεώσεων'
        
    def __str__(self):
        return self.name


class ObligationType(models.Model):
    """Τύπος υποχρέωσης"""
    
    FREQUENCY_CHOICES = [
        ('monthly', 'Μηνιαία'),
        ('quarterly', 'Τριμηνιαία'),
        ('annual', 'Ετήσια'),
        ('follows_vat', 'Ακολουθεί ΦΠΑ'),
    ]
    
    DEADLINE_TYPE_CHOICES = [
        ('last_day', 'Τελευταία ημέρα μήνα'),
        ('specific_day', 'Συγκεκριμένη ημέρα'),
        ('last_day_prev', 'Τελευταία προηγούμενου'),
        ('last_day_next', 'Τελευταία επόμενου'),
    ]
    
    name = models.CharField('Όνομα', max_length=100, unique=True)
    code = models.CharField('Κωδικός', max_length=50, unique=True)
    description = models.TextField('Περιγραφή', blank=True)
    
    frequency = models.CharField('Συχνότητα', max_length=20, choices=FREQUENCY_CHOICES)
    deadline_type = models.CharField('Τύπος Προθεσμίας', max_length=20, choices=DEADLINE_TYPE_CHOICES)
    deadline_day = models.IntegerField('Ημέρα Προθεσμίας', null=True, blank=True, help_text='Για συγκεκριμένη ημέρα')
    
    applicable_months = models.CharField('Μήνες Εφαρμογής', max_length=50, blank=True, 
                                         help_text='π.χ. 3,6,9,12 ή 1 για ετήσιες')
    
    exclusion_group = models.ForeignKey(ObligationGroup, on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name='Ομάδα Αλληλοαποκλεισμού',
                                       help_text='Υποχρεώσεις στην ίδια ομάδα αλληλοαποκλείονται')
    
    profiles = models.ManyToManyField(ObligationProfile, blank=True,
                                     verbose_name='Profiles Υποχρεώσεων',
                                     related_name='obligation_types',
                                     help_text='Σε ποια profiles ανήκει (μπορεί σε πολλά)')
    
    priority = models.IntegerField('Προτεραιότητα', default=0)
    is_active = models.BooleanField('Ενεργή', default=True)
    
    class Meta:
        verbose_name = 'Τύπος Υποχρέωσης'
        verbose_name_plural = 'Τύποι Υποχρεώσεων'
        ordering = ['priority', 'name']
        
    def __str__(self):
        return self.name
    
    def get_deadline_for_month(self, year, month):
        """Υπολογισμός deadline για συγκεκριμένο μήνα"""
        from calendar import monthrange
        
        if self.deadline_type == 'last_day':
            last_day = monthrange(year, month)[1]
            return timezone.datetime(year, month, last_day).date()
        
        elif self.deadline_type == 'last_day_prev':
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            last_day = monthrange(prev_year, prev_month)[1]
            return timezone.datetime(prev_year, prev_month, last_day).date()
        
        elif self.deadline_type == 'last_day_next':
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            last_day = monthrange(next_year, next_month)[1]
            return timezone.datetime(next_year, next_month, last_day).date()
        
        elif self.deadline_type == 'specific_day' and self.deadline_day:
            return timezone.datetime(year, month, self.deadline_day).date()
        
        return None
    
    def applies_to_month(self, month):
        """Ελέγχει αν η υποχρέωση ισχύει για συγκεκριμένο μήνα"""
        if self.frequency == 'monthly':
            return True

        if self.frequency == 'quarterly':
            # Τριμηνιαία: default μήνες 1,4,7,10 (υποβολή για προηγούμενο τρίμηνο)
            if self.applicable_months:
                applicable = [int(m.strip()) for m in self.applicable_months.split(',')]
            else:
                applicable = [1, 4, 7, 10]  # Default για τριμηνιαία
            return month in applicable

        if self.frequency == 'annual':
            # Ετήσια: αν έχει συγκεκριμένους μήνες, έλεγξε, αλλιώς επέτρεψε
            if self.applicable_months:
                applicable = [int(m.strip()) for m in self.applicable_months.split(',')]
                return month in applicable
            return True  # Χωρίς συγκεκριμένο μήνα, επέτρεψε δημιουργία

        return True  # Default: επέτρεψε για άλλες συχνότητες


class ClientObligation(models.Model):
    """Σύνδεση πελάτη με υποχρεώσεις"""
    client = models.OneToOneField(ClientProfile, on_delete=models.CASCADE, 
                                  related_name='obligation_settings',
                                  verbose_name='Πελάτης')
    obligation_types = models.ManyToManyField(ObligationType, blank=True, 
                                             verbose_name='Μεμονωμένες Υποχρεώσεις')
    obligation_profiles = models.ManyToManyField(ObligationProfile, blank=True,
                                                verbose_name='Profiles Υποχρεώσεων')
    is_active = models.BooleanField(default=True, verbose_name='Ενεργό')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ημ/νία Δημιουργίας')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ημ/νία Ενημέρωσης')
    
    class Meta:
        verbose_name = 'Υποχρεώσεις Πελάτη'
        verbose_name_plural = 'Υποχρεώσεις Πελατών'
        
    def __str__(self):
        return f"Υποχρεώσεις: {self.client.eponimia}"
    
    def get_all_obligation_types(self):
        """Επιστρέφει όλες τις υποχρεώσεις (μεμονωμένες + από profiles)"""
        obligations = set(self.obligation_types.all())

        for profile in self.obligation_profiles.all():
            obligations.update(profile.obligation_types.all())

        return list(obligations)


def get_safe_client_name(client):
    """Generate safe folder name from client: {afm}_{name}"""
    import re
    safe_name = re.sub(r'[^\w\s-]', '', client.eponimia)[:20]
    safe_name = safe_name.replace(' ', '_')
    return f"{client.afm}_{safe_name}"


def obligation_upload_path(instance, filename):
    """
    Generate organized upload path matching ArchiveConfiguration structure:
    clients/{afm}_{name}/{year}/{month}/{type_code}/{filename}

    This ensures ALL obligation files go to the same folder structure,
    whether uploaded via admin, wizard, or API.
    """
    ext = os.path.splitext(filename)[1].lower()

    # Build path components
    client_folder = get_safe_client_name(instance.client)
    year = str(instance.year)
    month = f"{instance.month:02d}"
    type_code = instance.obligation_type.code if instance.obligation_type else 'general'

    # Clean filename: {type}_{month}_{year}{ext}
    clean_name = f"{type_code}_{month}_{year}{ext}"

    # Final path: clients/{afm}_{name}/{year}/{month}/{type}/{filename}
    return os.path.join('clients', client_folder, year, month, type_code, clean_name)


class ArchiveConfiguration(models.Model):
    """Ρυθμίσεις αρχειοθέτησης ανά τύπο υποχρέωσης"""
    
    obligation_type = models.OneToOneField(
        ObligationType, 
        on_delete=models.CASCADE,
        related_name='archive_config'
    )
    
    filename_pattern = models.CharField(
        max_length=200,
        default='{type_code}_{month}_{year}.pdf',
        help_text='Variables: {year}, {month}, {day}, {client_afm}, {client_name}, {type_code}'
    )
    
    folder_pattern = models.CharField(
        max_length=200,
        default='clients/{client_afm}_{client_name}/{year}/{month}/{type_code}/',
        help_text='Folder structure pattern'
    )
    
    create_subfolder = models.BooleanField(default=False)
    subfolder_name = models.CharField(max_length=100, blank=True)
    allow_multiple_files = models.BooleanField(default=False)
    auto_rename = models.BooleanField(default=True)
    keep_original_name = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Ρύθμιση Αρχειοθέτησης'
        verbose_name_plural = 'Ρυθμίσεις Αρχειοθέτησης'
    
    def __str__(self):
        return f"Archive Config: {self.obligation_type.name}"
    
    def get_archive_path(self, obligation, filename=None):
        """
        Δημιουργεί το πλήρες path βάσει pattern.
        Default: clients/{afm}_{name}/{year}/{month}/{type_code}/{filename}
        """
        # Use shared helper for consistent client folder naming
        client_folder = get_safe_client_name(obligation.client)

        vars = {
            'year': str(obligation.year),
            'month': f'{obligation.month:02d}',
            'day': f'{obligation.deadline.day:02d}',
            'client_afm': obligation.client.afm,
            'client_name': client_folder.split('_', 1)[1] if '_' in client_folder else client_folder,
            'client_folder': client_folder,  # Full folder name: {afm}_{name}
            'type_code': obligation.obligation_type.code,
        }

        # Fix the patterns
        fixed_folder = self.folder_pattern.replace(':02d', '')
        fixed_filename = self.filename_pattern.replace(':02d', '')
        
        # Build folder
        folder = fixed_folder.format(**vars)
        if self.create_subfolder and self.subfolder_name:
            folder = os.path.join(folder, self.subfolder_name)
        
        # Build filename
        if filename and self.keep_original_name:
            final_filename = filename
        else:
            final_filename = fixed_filename.format(**vars)
        
        return os.path.join(folder, final_filename)


class MonthlyObligation(models.Model):
    """Μηνιαία εργασία υποχρέωσης"""
    
    STATUS_CHOICES = [
        ('pending', 'Εκκρεμεί'),
        ('completed', 'Ολοκληρώθηκε'),
        ('overdue', 'Καθυστερεί'),
    ]
    
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='monthly_obligations',
                              verbose_name='Πελάτης')
    obligation_type = models.ForeignKey(ObligationType, on_delete=models.CASCADE,
                                       verbose_name='Τύπος Υποχρέωσης')
    
    year = models.IntegerField('Έτος')
    month = models.IntegerField('Μήνας')
    deadline = models.DateField('Προθεσμία')
    
    status = models.CharField('Κατάσταση', max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_date = models.DateField('Ημ/νία Ολοκλήρωσης', null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Ολοκληρώθηκε από',
                                    related_name='completed_obligations')

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ανατεθειμένο σε',
        related_name='assigned_obligations'
    )

    notes = models.TextField('Σημειώσεις', blank=True)
    
    time_spent = models.DecimalField(
        'Χρόνος Εργασίας (ώρες)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='π.χ. 1.5 για 1 ώρα και 30 λεπτά'
    )
    hourly_rate = models.DecimalField(
        'Ωριαία Χρέωση (€)',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        default=50.00
    )

    # DEPRECATED: Τα αρχεία πλέον αποθηκεύονται στο ClientDocument
    # Τα πεδία κρατούνται προσωρινά για backwards compatibility
    attachment = models.FileField(
        upload_to=obligation_upload_path,
        blank=True,
        null=True,
        verbose_name='[DEPRECATED] Συνημμένο Αρχείο',
        help_text='Χρησιμοποιήστε ClientDocument αντί αυτού'
    )

    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text='[DEPRECATED] List of attachment paths - use ClientDocument'
    )

    created_at = models.DateTimeField('Δημιουργήθηκε', auto_now_add=True)
    updated_at = models.DateTimeField('Ενημερώθηκε', auto_now=True)
    
    class Meta:
        verbose_name = 'Μηνιαία Υποχρέωση'
        verbose_name_plural = 'Μηνιαίες Υποχρεώσεις'
        unique_together = ['client', 'obligation_type', 'year', 'month']
        ordering = ['deadline', 'client__eponimia']
        
    def __str__(self):
        return f"{self.client.eponimia} - {self.obligation_type.name} ({self.month}/{self.year})"
    
    @property
    def cost(self):
        """Υπολογισμός κόστους"""
        if self.time_spent and self.hourly_rate:
            return float(self.time_spent) * float(self.hourly_rate)
        return None
    
    @property
    def days_until_deadline(self):
        """Ημέρες μέχρι την προθεσμία"""
        if self.deadline:
            delta = self.deadline - timezone.now().date()
            return delta.days
        return 0
    
    @property
    def is_overdue(self):
        """Έλεγχος αν είναι καθυστερημένη"""
        return self.status != 'completed' and self.deadline < timezone.now().date()
    
    @property
    def deadline_status(self):
        """Status προθεσμίας για εμφάνιση"""
        days = self.days_until_deadline
        if self.status == 'completed':
            return 'completed'
        elif days < 0:
            return 'overdue'
        elif days == 0:
            return 'today'
        elif days <= 3:
            return 'urgent'
        else:
            return 'normal'
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_date:
            self.completed_date = timezone.now().date()
        
        if self.status != 'completed' and self.deadline < timezone.now().date():
            self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    # === Document Management Methods ===

    def get_documents(self, current_only=True):
        """
        Επιστρέφει τα έγγραφα αυτής της υποχρέωσης.

        Args:
            current_only: Αν True, επιστρέφει μόνο τις τρέχουσες εκδόσεις
        """
        qs = self.documents.all()
        if current_only:
            qs = qs.filter(is_current=True)
        return qs.order_by('-uploaded_at')

    def get_primary_document(self):
        """Επιστρέφει το κύριο έγγραφο (πρώτο τρέχον)"""
        return self.documents.filter(is_current=True).first()

    def has_documents(self):
        """Έλεγχος αν υπάρχουν έγγραφα"""
        return self.documents.filter(is_current=True).exists()

    @property
    def documents_count(self):
        """Αριθμός τρεχόντων εγγράφων"""
        return self.documents.filter(is_current=True).count()

    def add_document(self, uploaded_file, user=None, description=''):
        """
        Προσθήκη νέου εγγράφου στην υποχρέωση.

        Αν υπάρχει ήδη έγγραφο, ρωτάει αν θέλει να δημιουργήσει νέα έκδοση.
        Αυτός ο έλεγχος γίνεται στο view/admin, όχι εδώ.

        Args:
            uploaded_file: Το αρχείο που ανέβηκε
            user: Ο χρήστης που το ανέβασε
            description: Περιγραφή

        Returns:
            ClientDocument instance
        """
        # Import here to avoid circular import
        from accounting.models import ClientDocument

        doc = ClientDocument(
            client=self.client,
            obligation=self,
            file=uploaded_file,
            original_filename=os.path.basename(uploaded_file.name),
            description=description,
            uploaded_by=user,
            year=self.year,
            month=self.month,
        )
        doc.save()
        return doc

    def get_email_attachments(self):
        """
        Επιστρέφει λίστα αρχείων για αποστολή email.
        Χρησιμοποιείται από το email system.
        """
        attachments = []
        for doc in self.get_documents():
            if doc.file:
                try:
                    attachments.append(doc.file.path)
                except (ValueError, FileNotFoundError):
                    pass
        return attachments

    @property
    def folder_path(self):
        """Επιστρέφει το path του φακέλου για αυτή την υποχρέωση"""
        client_folder = get_client_folder(self.client)
        category = self.obligation_type.code if self.obligation_type else 'general'
        return os.path.join(
            settings.MEDIA_ROOT,
            client_folder,
            str(self.year),
            f"{self.month:02d}",
            category
        )


class EmailTemplate(models.Model):
    """
    Πρότυπα Email με υποστήριξη {variable} syntax.

    Διαθέσιμες μεταβλητές:
    - {client_name} - Επωνυμία πελάτη
    - {client_afm} - ΑΦΜ πελάτη
    - {client_email} - Email πελάτη
    - {obligation_type} - Τύπος υποχρέωσης
    - {period_month} - Μήνας περιόδου (αριθμός)
    - {period_year} - Έτος περιόδου
    - {period_display} - Μήνας/Έτος (π.χ. "01/2025")
    - {deadline} - Προθεσμία (μορφή ημερομηνίας)
    - {completed_date} - Ημερομηνία ολοκλήρωσης
    - {accountant_name} - Όνομα λογιστή
    - {company_name} - Όνομα εταιρείας
    """

    name = models.CharField('Όνομα Προτύπου', max_length=200)
    description = models.TextField('Περιγραφή', blank=True)
    subject = models.CharField('Θέμα Email', max_length=500,
        help_text='Υποστηρίζει μεταβλητές: {client_name}, {obligation_type}, {period_month}/{period_year}')
    body_html = models.TextField('Κείμενο (HTML)',
        help_text='Υποστηρίζει μεταβλητές: {client_name}, {client_afm}, {obligation_type}, {deadline}, {completed_date}, {accountant_name}')

    # Optional: Auto-select for specific obligation type
    obligation_type = models.ForeignKey(
        ObligationType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Τύπος Υποχρέωσης (αυτόματη επιλογή)',
        help_text='Αν οριστεί, αυτό το template επιλέγεται αυτόματα για αυτόν τον τύπο υποχρέωσης'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField('Ενεργό', default=True)

    class Meta:
        verbose_name = 'Πρότυπο Email'
        verbose_name_plural = 'Πρότυπα Email'
        ordering = ['name']

    def __str__(self):
        return self.name

    def render(self, context):
        """
        Render template with context variables using Django Template syntax.
        Legacy method for backwards compatibility.
        """
        from django.template import Template, Context
        subject_template = Template(self.subject)
        body_template = Template(self.body_html)

        rendered_subject = subject_template.render(Context(context))
        rendered_body = body_template.render(Context(context))

        return rendered_subject, rendered_body

    def render_simple(self, variables):
        """
        Render template with simple {variable} replacement.

        Args:
            variables: dict with keys like 'client_name', 'obligation_type', etc.

        Returns:
            tuple: (rendered_subject, rendered_body)
        """
        subject = self.subject
        body = self.body_html

        # Replace all variables
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            subject = subject.replace(placeholder, str(value) if value else '')
            body = body.replace(placeholder, str(value) if value else '')

        return subject, body

    @classmethod
    def get_template_for_obligation(cls, obligation):
        """
        Get the appropriate template for an obligation.
        First tries to find a template specific to the obligation type,
        then falls back to a default template.
        """
        # Try to find template specific to obligation type
        template = cls.objects.filter(
            is_active=True,
            obligation_type=obligation.obligation_type
        ).first()

        if template:
            return template

        # Fall back to default template (name contains "Ολοκλήρωση" or is first active)
        template = cls.objects.filter(
            is_active=True,
            name__icontains='Ολοκλήρωση'
        ).first()

        if template:
            return template

        # Last resort: any active template
        return cls.objects.filter(is_active=True).first()

    @staticmethod
    def get_available_variables():
        """Return list of available variables for UI display"""
        return [
            ('{client_name}', 'Επωνυμία πελάτη'),
            ('{client_afm}', 'ΑΦΜ πελάτη'),
            ('{client_email}', 'Email πελάτη'),
            ('{obligation_type}', 'Τύπος υποχρέωσης'),
            ('{period_month}', 'Μήνας περιόδου'),
            ('{period_year}', 'Έτος περιόδου'),
            ('{period_display}', 'Περίοδος (ΜΜ/ΕΕΕΕ)'),
            ('{deadline}', 'Προθεσμία'),
            ('{completed_date}', 'Ημερομηνία ολοκλήρωσης'),
            ('{accountant_name}', 'Όνομα λογιστή'),
            ('{company_name}', 'Όνομα εταιρείας'),
        ]


class EmailLog(models.Model):
    """
    Ιστορικό αποσταλμένων email.
    Καταγράφει κάθε email που στέλνεται από το σύστημα.
    """

    STATUS_CHOICES = [
        ('sent', 'Απεστάλη'),
        ('failed', 'Αποτυχία'),
        ('pending', 'Σε αναμονή'),
        ('queued', 'Στην ουρά'),
    ]

    recipient_email = models.EmailField('Email Παραλήπτη')
    recipient_name = models.CharField('Όνομα Παραλήπτη', max_length=200)

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
        verbose_name='Πελάτης'
    )

    obligation = models.ForeignKey(
        'MonthlyObligation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
        verbose_name='Υποχρέωση'
    )

    template_used = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Πρότυπο'
    )

    subject = models.CharField('Θέμα', max_length=500)
    body = models.TextField('Κείμενο')

    status = models.CharField(
        'Κατάσταση',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField('Μήνυμα Σφάλματος', blank=True)
    retry_count = models.PositiveIntegerField('Αριθμός Επαναπροσπαθειών', default=0)

    sent_at = models.DateTimeField('Αποστολή', auto_now_add=True)
    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_emails',
        verbose_name='Αποστολέας'
    )

    class Meta:
        verbose_name = 'Ιστορικό Email'
        verbose_name_plural = 'Ιστορικό Email'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['client', '-sent_at']),
            models.Index(fields=['status', '-sent_at']),
            models.Index(fields=['-sent_at']),
        ]

    def __str__(self):
        status_icon = {'sent': '✅', 'failed': '❌', 'pending': '⏳', 'queued': '📤'}.get(self.status, '?')
        return f"{status_icon} {self.recipient_email} - {self.subject[:50]}"

    @property
    def status_display(self):
        """Return status with icon"""
        icons = {'sent': '✅', 'failed': '❌', 'pending': '⏳', 'queued': '📤'}
        return f"{icons.get(self.status, '?')} {self.get_status_display()}"


class EmailAutomationRule(models.Model):
    """Κανόνες Αυτοματοποίησης Email"""
    
    TRIGGER_CHOICES = (
        ('on_complete', 'Όταν ολοκληρώνεται υποχρέωση'),
        ('before_deadline', 'Πριν την προθεσμία'),
        ('on_overdue', 'Όταν καθυστερεί'),
        ('manual', 'Χειροκίνητα'),
    )
    
    TIMING_CHOICES = (
        ('immediate', '⚡ Άμεσα'),
        ('delay_1h', '⏰ Μετά από 1 ώρα'),
        ('delay_24h', '📅 Επόμενη ημέρα'),
        ('scheduled', '🕐 Συγκεκριμένη ώρα'),
    )
    
    name = models.CharField('Όνομα Κανόνα', max_length=200)
    description = models.TextField('Περιγραφή', blank=True)
    
    trigger = models.CharField('Trigger', max_length=50, choices=TRIGGER_CHOICES)
    filter_obligation_types = models.ManyToManyField(
        ObligationType,
        blank=True,
        verbose_name='Φίλτρο Τύπων Υποχρέωσης',
        help_text='Αν άδειο, ισχύει για όλους τους τύπους'
    )
    
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE,
        verbose_name='Πρότυπο Email'
    )
    
    timing = models.CharField('Χρονοδιάγραμμα', max_length=50, choices=TIMING_CHOICES, default='immediate')
    scheduled_time = models.TimeField('Ώρα Αποστολής', null=True, blank=True, help_text='Για timing "Συγκεκριμένη ώρα"')
    days_before_deadline = models.IntegerField('Ημέρες πριν την προθεσμία', null=True, blank=True)
    
    is_active = models.BooleanField('Ενεργός', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Κανόνας Αυτοματοποίησης'
        verbose_name_plural = 'Κανόνες Αυτοματοποίησης'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_display()})"
    
    def matches_obligation(self, obligation):
        """Check if rule applies to this obligation"""
        if not self.is_active:
            return False
        
        if self.filter_obligation_types.exists():
            return obligation.obligation_type in self.filter_obligation_types.all()
        
        return True


class ScheduledEmail(models.Model):
    """Προγραμματισμένα Email - Υποστηρίζει πολλαπλούς παραλήπτες μέσω BCC"""

    STATUS_CHOICES = (
        ('pending', '⏳ Εκκρεμεί'),
        ('sent', '✅ Στάλθηκε'),
        ('failed', '❌ Απέτυχε'),
        ('cancelled', '🚫 Ακυρώθηκε'),
    )

    # Υποστηρίζει πολλαπλά emails (χωρισμένα με κόμμα ή νέα γραμμή)
    recipient_email = models.TextField(
        'Email Παραλήπτη/ών',
        help_text='Πολλαπλά emails χωρισμένα με κόμμα ή νέα γραμμή'
    )
    recipient_name = models.TextField(
        'Όνομα Παραλήπτη/ών',
        help_text='Πολλαπλά ονόματα χωρισμένα με κόμμα ή νέα γραμμή',
        blank=True,
        default=''
    )
    
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Πελάτης'
    )
    
    obligations = models.ManyToManyField(
        MonthlyObligation,
        verbose_name='Υποχρεώσεις',
        help_text='Οι υποχρεώσεις που αφορά το email'
    )
    
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Πρότυπο'
    )
    
    automation_rule = models.ForeignKey(
        EmailAutomationRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Κανόνας Αυτοματοποίησης'
    )
    
    subject = models.CharField('Θέμα', max_length=500)
    body_html = models.TextField('Κείμενο')
    
    send_at = models.DateTimeField('Αποστολή στις', db_index=True)
    sent_at = models.DateTimeField('Στάλθηκε στις', null=True, blank=True)
    
    status = models.CharField('Κατάσταση', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField('Μήνυμα Σφάλματος', blank=True)
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='scheduled_emails',
        verbose_name='Δημιουργήθηκε από'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Προγραμματισμένο Email'
        verbose_name_plural = 'Προγραμματισμένα Email'
        ordering = ['send_at']
    
    def __str__(self):
        count = self.recipient_count
        if count == 1:
            display = self.recipient_name or self.recipient_email
        else:
            display = f"{count} παραλήπτες"
        return f"{display} - {self.subject} ({self.send_at.strftime('%d/%m/%Y %H:%M')})"
    
    def get_attachments(self):
        """
        Get all attachments from obligations.
        Uses the new unified ClientDocument system.
        """
        attachments = []
        for obl in self.obligations.all():
            # New: Use get_email_attachments() which returns file paths
            obl_attachments = obl.get_email_attachments()
            attachments.extend(obl_attachments)
        return attachments
    
    def mark_as_sent(self):
        """Mark email as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error):
        """Mark email as failed"""
        self.status = 'failed'
        self.error_message = str(error)
        self.save()

    def get_recipients_list(self):
        """
        Επιστρέφει λίστα έγκυρων email διευθύνσεων.
        Αναλύει το recipient_email πεδίο που μπορεί να περιέχει
        πολλαπλά emails χωρισμένα με κόμμα ή νέα γραμμή.
        """
        import re
        if not self.recipient_email:
            return []

        # Χώρισμα με κόμμα ή νέα γραμμή
        raw_emails = re.split(r'[,\n\r]+', self.recipient_email)

        # Καθαρισμός και επικύρωση
        valid_emails = []
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        for email in raw_emails:
            email = email.strip()
            if email and email_pattern.match(email):
                valid_emails.append(email)

        return valid_emails

    @property
    def recipient_count(self):
        """Επιστρέφει τον αριθμό των παραληπτών"""
        return len(self.get_recipients_list())

    def get_recipients_display(self):
        """Επιστρέφει περιληπτική εμφάνιση παραληπτών για admin"""
        recipients = self.get_recipients_list()
        count = len(recipients)
        if count == 0:
            return "Κανένας παραλήπτης"
        elif count == 1:
            return recipients[0]
        elif count <= 3:
            return ", ".join(recipients)
        else:
            return f"{recipients[0]}, {recipients[1]} (+{count - 2} ακόμα)"


class EmailSettings(models.Model):
    """
    Ρυθμίσεις Email - Singleton model για αποθήκευση SMTP settings στη βάση.
    Μπορεί να παρακαμφθεί από environment variables.
    """

    SECURITY_CHOICES = [
        ('tls', 'TLS (port 587)'),
        ('ssl', 'SSL (port 465)'),
        ('none', 'Κανένα (port 25)'),
    ]

    # SMTP Settings
    smtp_host = models.CharField(
        'SMTP Server',
        max_length=255,
        default='smtp.gmail.com',
        help_text='π.χ. smtp.gmail.com, mail.example.com'
    )
    smtp_port = models.PositiveIntegerField(
        'SMTP Port',
        default=587,
        help_text='Συνήθως 587 (TLS), 465 (SSL), ή 25'
    )
    smtp_username = models.CharField(
        'SMTP Username',
        max_length=255,
        blank=True,
        default='',
        help_text='Συνήθως το email σας'
    )
    # Password is stored encrypted using Fernet
    _encrypted_smtp_password = models.TextField(
        'SMTP Password (encrypted)',
        blank=True,
        default='',
        help_text='App Password για Gmail/Google Workspace (κρυπτογραφημένο)'
    )
    smtp_security = models.CharField(
        'Ασφάλεια',
        max_length=10,
        choices=SECURITY_CHOICES,
        default='tls'
    )

    # Sender Info
    from_email = models.EmailField(
        'Email Αποστολέα',
        help_text='Η διεύθυνση που θα εμφανίζεται ως αποστολέας'
    )
    from_name = models.CharField(
        'Όνομα Αποστολέα',
        max_length=100,
        blank=True,
        default='',
        help_text='π.χ. Λογιστικό Γραφείο Παπαδόπουλος'
    )
    reply_to = models.EmailField(
        'Reply-To Email',
        blank=True,
        default='',
        help_text='Αν διαφέρει από το email αποστολέα'
    )

    # Company Info (for templates)
    company_name = models.CharField(
        'Όνομα Εταιρείας',
        max_length=200,
        blank=True,
        default=''
    )
    company_phone = models.CharField(
        'Τηλέφωνο Εταιρείας',
        max_length=50,
        blank=True,
        default=''
    )
    company_website = models.URLField(
        'Website Εταιρείας',
        blank=True,
        default=''
    )
    accountant_name = models.CharField(
        'Όνομα Λογιστή',
        max_length=100,
        blank=True,
        default=''
    )
    accountant_title = models.CharField(
        'Τίτλος Λογιστή',
        max_length=100,
        blank=True,
        default='Λογιστής Α\' Τάξης',
        help_text='π.χ. Λογιστής Α\' Τάξης, Ορκωτός Ελεγκτής'
    )

    # Email Signature
    email_signature = models.TextField(
        'Υπογραφή Email',
        blank=True,
        default='',
        help_text='HTML υπογραφή που προστίθεται στα emails'
    )

    # Rate Limiting
    rate_limit = models.FloatField(
        'Rate Limit (emails/sec)',
        default=2.0,
        help_text='Μέγιστα emails ανά δευτερόλεπτο'
    )
    burst_limit = models.PositiveIntegerField(
        'Burst Limit',
        default=5,
        help_text='Μέγιστα emails σε burst'
    )

    # Status
    is_active = models.BooleanField(
        'Ενεργό',
        default=True,
        help_text='Αν απενεργοποιηθεί, τα emails δεν θα στέλνονται'
    )
    last_test_at = models.DateTimeField(
        'Τελευταίο Test',
        null=True,
        blank=True
    )
    last_test_success = models.BooleanField(
        'Επιτυχές Test',
        null=True,
        blank=True
    )
    last_test_error = models.TextField(
        'Σφάλμα Test',
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def smtp_password(self):
        """Get decrypted SMTP password"""
        if not self._encrypted_smtp_password:
            return ''
        try:
            from mydata.encryption import decrypt_value, is_encrypted
            if is_encrypted(self._encrypted_smtp_password):
                return decrypt_value(self._encrypted_smtp_password)
            # Return as-is if not encrypted (legacy/migration)
            return self._encrypted_smtp_password
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to decrypt SMTP password: {e}")
            return ''

    @smtp_password.setter
    def smtp_password(self, value):
        """Set SMTP password (will be encrypted on save)"""
        if not value:
            self._encrypted_smtp_password = ''
            return
        try:
            from mydata.encryption import encrypt_value, is_encrypted
            if is_encrypted(value):
                # Already encrypted, store as-is
                self._encrypted_smtp_password = value
            else:
                # Encrypt plain text
                self._encrypted_smtp_password = encrypt_value(value)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to encrypt SMTP password: {e}")
            # Store plain text as fallback (not recommended)
            self._encrypted_smtp_password = value

    class Meta:
        verbose_name = 'Ρυθμίσεις Email'
        verbose_name_plural = 'Ρυθμίσεις Email'

    def __str__(self):
        return f"Email Settings ({self.from_email})"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        if not self.pk and EmailSettings.objects.exists():
            # Update existing instead of creating new
            existing = EmailSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """
        Get or create email settings.
        Falls back to environment variables if no DB settings exist.
        """
        settings_obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'smtp_host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                'smtp_port': getattr(settings, 'EMAIL_PORT', 587),
                'smtp_username': getattr(settings, 'EMAIL_HOST_USER', ''),
                # Password will be set separately via property setter
                'smtp_security': 'tls' if getattr(settings, 'EMAIL_USE_TLS', True) else ('ssl' if getattr(settings, 'EMAIL_USE_SSL', False) else 'none'),
                'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
                'from_name': getattr(settings, 'COMPANY_NAME', ''),
                'company_name': getattr(settings, 'COMPANY_NAME', ''),
                'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
                'company_website': getattr(settings, 'COMPANY_WEBSITE', ''),
                'accountant_name': getattr(settings, 'ACCOUNTANT_NAME', ''),
                'accountant_title': getattr(settings, 'ACCOUNTANT_TITLE', ''),
                'email_signature': getattr(settings, 'EMAIL_SIGNATURE', ''),
            }
        )
        if created:
            # Set password via property to encrypt it
            env_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            if env_password:
                settings_obj.smtp_password = env_password
                settings_obj.save(update_fields=['_encrypted_smtp_password'])
        return settings_obj

    def get_smtp_config(self):
        """Return SMTP configuration dict for Django email backend"""
        return {
            'host': self.smtp_host,
            'port': self.smtp_port,
            'username': self.smtp_username,
            'password': self.smtp_password,
            'use_tls': self.smtp_security == 'tls',
            'use_ssl': self.smtp_security == 'ssl',
        }

    def test_connection(self):
        """
        Test SMTP connection and update status.
        Returns (success: bool, message: str)
        """
        import smtplib
        from socket import timeout as SocketTimeout

        self.last_test_at = timezone.now()

        try:
            # Create connection based on security type
            if self.smtp_security == 'ssl':
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                if self.smtp_security == 'tls':
                    server.starttls()

            # Try to login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            server.quit()

            self.last_test_success = True
            self.last_test_error = ''
            self.save()
            return True, 'Η σύνδεση SMTP επιτυχής!'

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f'Σφάλμα authentication: {e}'
            self.last_test_success = False
            self.last_test_error = error_msg
            self.save()
            return False, error_msg

        except smtplib.SMTPConnectError as e:
            error_msg = f'Αδυναμία σύνδεσης στον server: {e}'
            self.last_test_success = False
            self.last_test_error = error_msg
            self.save()
            return False, error_msg

        except SocketTimeout:
            error_msg = 'Timeout κατά τη σύνδεση - ελέγξτε host/port'
            self.last_test_success = False
            self.last_test_error = error_msg
            self.save()
            return False, error_msg

        except Exception as e:
            error_msg = f'Σφάλμα: {str(e)}'
            self.last_test_success = False
            self.last_test_error = error_msg
            self.save()
            return False, error_msg


class VoIPCall(models.Model):
    """Καταγραφή κλήσεων VoIP/Fritz!Box"""
    
    DIRECTION_CHOICES = [
        ('incoming', 'Εισερχόμενη'),
        ('outgoing', 'Εξερχόμενη'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ενεργή'),
        ('completed', 'Ολοκληρώθηκε'),
        ('missed', 'Αναπάντητη'),
        ('failed', 'Αποτυχία'),
    ]
    
    RESOLUTION_CHOICES = [
        ('pending', '⏳ Εκρεμμότητα'),
        ('closed', '✅ Κλειστή'),
        ('follow_up', '📞 Follow-up'),
    ]
    
    call_id = models.CharField('ID Κλήσης', max_length=50, unique=True)
    phone_number = models.CharField('Αριθμός Τηλεφώνου', max_length=20)
    direction = models.CharField('Κατεύθυνση', max_length=20, choices=DIRECTION_CHOICES)
    status = models.CharField('Κατάσταση', max_length=20, choices=STATUS_CHOICES, default='active')
    
    started_at = models.DateTimeField('Ώρα Έναρξης')
    ended_at = models.DateTimeField('Ώρα Λήξης', null=True, blank=True)
    duration_seconds = models.IntegerField('Διάρκεια (δευτερόλεπτα)', default=0)
    
    client = models.ForeignKey(
        'ClientProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voip_calls',
        verbose_name='Πελάτης'
    )
    client_email = models.EmailField('Email Πελάτη', blank=True, null=True)
    
    notes = models.TextField('Σημειώσεις', blank=True)
    resolution = models.CharField('Ευστάθεια', max_length=20, choices=RESOLUTION_CHOICES, default='pending', blank=True)
    
    ticket_created = models.BooleanField('Τίκετ Δημιουργήθηκε', default=False)
    ticket_id = models.CharField('ID Τίκετ', max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField('Καταγραφή', auto_now_add=True)
    updated_at = models.DateTimeField('Ενημέρωση', auto_now=True)
    
    class Meta:
        verbose_name = 'Κλήση VoIP'
        verbose_name_plural = 'Κλήσεις VoIP'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['call_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['client']),
        ]
    
    def __str__(self):
        client_name = self.client.eponimia if self.client else 'Άγνωστος'
        return f"{self.get_direction_display()} - {self.phone_number} ({client_name})"
    
    @property
    def duration_formatted(self):
        """Επιστρέφει τη διάρκεια σε ευανάγνωστη μορφή"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @property
    def is_missed(self):
        return self.status == 'missed'
    
    def save(self, *args, **kwargs):
        if self.ended_at and self.started_at:
            delta = self.ended_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
        super().save(*args, **kwargs)


class VoIPCallLog(models.Model):
    """Καταγραφή ιστορικού αλλαγών κλήσεων"""
    
    ACTION_CHOICES = [
        ('started', 'Έναρξη'),
        ('ended', 'Λήξη'),
        ('ticket_created', 'Δημιουργία τίκετ'),
        ('client_matched', 'Σύνδεση με πελάτη'),
        ('status_changed', 'Αλλαγή κατάστασης'),
    ]
    
    call = models.ForeignKey(
        VoIPCall,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Κλήση'
    )
    
    action = models.CharField('Ενέργεια', max_length=50, choices=ACTION_CHOICES)
    description = models.TextField('Περιγραφή', blank=True)
    created_at = models.DateTimeField('Χρονοσήμανση', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Καταγραφή Κλήσης'
        verbose_name_plural = 'Καταγραφές Κλήσεων'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.call.phone_number} - {self.get_action_display()}"


class Ticket(models.Model):
    """Αυτόματα δημιουργούμενα tickets από missed calls"""
    
    STATUS_CHOICES = [
        ('open', '🔴 Ανοιχτό'),
        ('assigned', '👤 Ανατεθειμένο'),
        ('in_progress', '⏳ Σε εξέλιξη'),
        ('resolved', '✅ Επιλυμένο'),
        ('closed', '🔒 Κλειστό'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '🟢 Χαμηλή'),
        ('medium', '🟡 Μέση'),
        ('high', '🔴 Υψηλή'),
        ('urgent', '🚨 Επείγουσα'),
    ]
    
    call = models.OneToOneField(
        VoIPCall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket',
        verbose_name='Κλήση'
    )
    
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voip_tickets',
        verbose_name='Πελάτης'
    )
    
    title = models.CharField(
        'Τίτλος',
        max_length=200,
        help_text='Αυτόματα συμπληρώνεται'
    )
    
    description = models.TextField(
        'Περιγραφή',
        blank=True,
        help_text='Λεπτομέρειες για τη κλήση'
    )
    
    status = models.CharField(
        'Κατάσταση',
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    
    priority = models.CharField(
        'Προτεραιότητα',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='high'
    )
    
    assigned_to = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='Ανατεθειμένο σε'
    )
    
    notes = models.TextField(
        'Σημειώσεις',
        blank=True,
        help_text='Εσωτερικές σημειώσεις'
    )
    
    created_at = models.DateTimeField('Δημιουργήθηκε', auto_now_add=True)
    assigned_at = models.DateTimeField('Ανατέθηκε', null=True, blank=True)
    resolved_at = models.DateTimeField('Επιλύθηκε', null=True, blank=True)
    closed_at = models.DateTimeField('Κλειστό', null=True, blank=True)
    
    email_sent = models.BooleanField('Email στάλθηκε', default=False)
    follow_up_scheduled = models.BooleanField('Follow-up Προγραμματισμένο', default=False)
    
    class Meta:
        verbose_name = 'Ticket (Missed Call)'
        verbose_name_plural = 'Tickets (Missed Calls)'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"#{self.id} - {self.title}"
    
    def mark_as_assigned(self, user):
        """Mark ticket as assigned"""
        self.status = 'assigned'
        self.assigned_to = user
        self.assigned_at = timezone.now()
        self.save()
    
    def mark_as_in_progress(self):
        """Mark ticket as in progress"""
        self.status = 'in_progress'
        self.save()
        return self
    
    def mark_as_resolved(self):
        """Mark ticket as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def mark_as_closed(self):
        """Mark ticket as closed"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()
    
    @property
    def is_open(self):
        return self.status in ['open', 'assigned', 'in_progress']
    
    @property
    def is_resolved(self):
        return self.status in ['resolved', 'closed']
    
    @property
    def days_since_created(self):
        """Days since ticket creation"""
        return (timezone.now() - self.created_at).days
    
    @property
    def response_time_seconds(self):
        """How many seconds until first assignment"""
        if self.assigned_at:
            return int((self.assigned_at - self.created_at).total_seconds())
        return None


def get_client_folder(client):
    """
    Base folder path του πελάτη.
    Pattern: clients/{ΑΦΜ}_{Επωνυμία}/
    """
    import re
    # Καθαρισμός επωνυμίας - κρατάμε μόνο alphanumeric και ελληνικά
    safe_name = re.sub(r'[^\w\s-]', '', client.eponimia)[:20]
    safe_name = safe_name.replace(' ', '_').strip('_')
    return os.path.join('clients', f"{client.afm}_{safe_name}")


def client_document_path(instance, filename):
    """
    Ενιαίο path για όλα τα έγγραφα πελατών.

    Υποστηρίζει 3 τύπους φακέλων:
    - permanent: clients/{ΑΦΜ}_{Επωνυμία}/00_ΜΟΝΙΜΑ/{category}/{filename}
    - monthly:   clients/{ΑΦΜ}_{Επωνυμία}/{YYYY}/{MM}/{category}/{filename}
    - yearend:   clients/{ΑΦΜ}_{Επωνυμία}/{YYYY}/13_ΕΤΗΣΙΑ/{category}/{filename}

    Χρησιμοποιεί τις ρυθμίσεις από FilingSystemSettings αν υπάρχουν.
    """
    from settings.models import FilingSystemSettings

    client_folder = get_client_folder(instance.client)
    category = instance.document_category if instance.document_category else 'general'

    # Λήψη ρυθμίσεων
    try:
        settings = FilingSystemSettings.get_settings()
    except Exception:
        settings = None

    # Προσδιορισμός τύπου φακέλου
    folder_type = 'monthly'  # default
    if hasattr(instance, 'CATEGORY_FOLDER_TYPE'):
        folder_type = instance.CATEGORY_FOLDER_TYPE.get(category, 'monthly')

    # === ΜΟΝΙΜΟΣ ΦΑΚΕΛΟΣ ===
    if folder_type == 'permanent':
        permanent_name = '00_ΜΟΝΙΜΑ'
        if settings and settings.enable_permanent_folder:
            permanent_name = settings.permanent_folder_name
        return os.path.join(client_folder, permanent_name, category, filename)

    # Χρήση year/month από obligation αν υπάρχει, αλλιώς τρέχουσα ημερομηνία
    if instance.obligation:
        year = str(instance.obligation.year)
        month = instance.obligation.month
    else:
        now = datetime.now()
        year = str(now.year)
        month = now.month

    # === ΕΤΗΣΙΟΣ ΦΑΚΕΛΟΣ (13_ΕΤΗΣΙΑ) ===
    if folder_type == 'yearend':
        yearend_name = '13_ΕΤΗΣΙΑ'
        if settings and settings.enable_yearend_folder:
            yearend_name = settings.yearend_folder_name
        return os.path.join(client_folder, year, yearend_name, category, filename)

    # === ΜΗΝΙΑΙΟΣ ΦΑΚΕΛΟΣ ===
    # Μορφοποίηση μήνα
    if settings and settings.use_greek_month_names:
        month_str = settings.get_month_folder_name(month)
    else:
        month_str = f"{month:02d}"

    return os.path.join(client_folder, year, month_str, category, filename)


class ClientDocument(models.Model):
    """
    Ενιαίο model για όλα τα έγγραφα πελατών.

    Χρησιμοποιείται τόσο για γενικά έγγραφα όσο και για
    συνημμένα υποχρεώσεων. Υποστηρίζει versioning.
    """

    # === Κατηγορίες Εγγράφων ===
    # Μόνιμα (00_ΜΟΝΙΜΑ)
    PERMANENT_CATEGORIES = [
        ('registration', 'Ιδρυτικά Έγγραφα'),
        ('contracts', 'Συμβάσεις'),
        ('licenses', 'Άδειες & Πιστοποιητικά'),
        ('correspondence', 'Αλληλογραφία'),
    ]

    # Μηνιαία
    MONTHLY_CATEGORIES = [
        ('vat', 'ΦΠΑ'),
        ('apd', 'ΑΠΔ/ΕΦΚΑ'),
        ('myf', 'ΜΥΦ'),
        ('payroll', 'Μισθοδοσία'),
        ('invoices_issued', 'Εκδοθέντα Τιμολόγια'),
        ('invoices_received', 'Ληφθέντα Τιμολόγια'),
        ('bank', 'Τραπεζικά'),
        ('receipts', 'Αποδείξεις'),
    ]

    # Ετήσια (13_ΕΤΗΣΙΑ)
    YEAREND_CATEGORIES = [
        ('e1', 'Ε1 - Φόρος Εισοδήματος'),
        ('e2', 'Ε2 - Ακίνητα'),
        ('e3', 'Ε3 - Οικονομικά Στοιχεία'),
        ('enfia', 'ΕΝΦΙΑ'),
        ('balance', 'Ισολογισμός'),
        ('audit', 'Έλεγχοι'),
    ]

    # Backwards compatible - όλες οι κατηγορίες
    CATEGORY_CHOICES = (
        PERMANENT_CATEGORIES +
        MONTHLY_CATEGORIES +
        YEAREND_CATEGORIES +
        [
            # Legacy categories για συμβατότητα
            ('invoices', 'Τιμολόγια'),  # Deprecated: χρήση invoices_issued/received
            ('tax', 'Φορολογικά'),      # Deprecated: χρήση e1/e2/e3
            ('efka', 'ΕΦΚΑ'),           # Deprecated: χρήση apd
            ('general', 'Γενικά'),
        ]
    )

    # Mapping κατηγοριών σε τύπο φακέλου
    CATEGORY_FOLDER_TYPE = {
        'registration': 'permanent',
        'contracts': 'permanent',
        'licenses': 'permanent',
        'correspondence': 'permanent',
        'vat': 'monthly',
        'apd': 'monthly',
        'myf': 'monthly',
        'payroll': 'monthly',
        'invoices_issued': 'monthly',
        'invoices_received': 'monthly',
        'bank': 'monthly',
        'receipts': 'monthly',
        'e1': 'yearend',
        'e2': 'yearend',
        'e3': 'yearend',
        'enfia': 'yearend',
        'balance': 'yearend',
        'audit': 'yearend',
        'general': 'monthly',
        'invoices': 'monthly',
        'tax': 'yearend',
        'efka': 'monthly',
    }

    # === Σχέσεις ===
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Πελάτης'
    )
    obligation = models.ForeignKey(
        MonthlyObligation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='documents',
        verbose_name='Υποχρέωση'
    )

    # === Αρχείο ===
    file = models.FileField(
        upload_to=client_document_path,
        verbose_name='Αρχείο'
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name='Αρχικό Όνομα',
        help_text='Το όνομα του αρχείου όπως ανέβηκε'
    )
    filename = models.CharField(
        max_length=255,
        verbose_name='Όνομα Αρχείου'
    )
    file_type = models.CharField(
        max_length=50,
        verbose_name='Τύπος'
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name='Μέγεθος (bytes)'
    )

    # === Κατηγοριοποίηση ===
    document_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        db_index=True,
        verbose_name='Κατηγορία'
    )

    # === Χρονικά στοιχεία για filtering ===
    year = models.PositiveIntegerField(
        verbose_name='Έτος',
        db_index=True,
        help_text='Έτος αναφοράς (από υποχρέωση ή upload)'
    )
    month = models.PositiveIntegerField(
        verbose_name='Μήνας',
        db_index=True,
        help_text='Μήνας αναφοράς (από υποχρέωση ή upload)'
    )

    # === Versioning ===
    version = models.PositiveIntegerField(
        default=1,
        verbose_name='Έκδοση'
    )
    is_current = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Τρέχουσα Έκδοση'
    )
    previous_version = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_versions',
        verbose_name='Προηγούμενη Έκδοση'
    )

    # === Metadata ===
    description = models.TextField(
        blank=True,
        verbose_name='Περιγραφή'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ημ/νία Upload'
    )
    uploaded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='uploaded_documents',
        verbose_name='Ανέβηκε από'
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Έγγραφο Πελάτη'
        verbose_name_plural = 'Έγγραφα Πελατών'
        indexes = [
            models.Index(fields=['client', 'year', 'month']),
            models.Index(fields=['client', 'document_category']),
            models.Index(fields=['obligation', 'is_current']),
        ]

    def __str__(self):
        version_str = f" (v{self.version})" if self.version > 1 else ""
        return f"{self.filename}{version_str} - {self.client.eponimia}"

    def save(self, *args, **kwargs):
        # Auto-extract file info
        if self.file:
            # Κρατάμε το αρχικό όνομα
            if not self.original_filename:
                self.original_filename = os.path.basename(self.file.name)

            self.filename = os.path.basename(self.file.name)
            self.file_type = self.filename.split('.')[-1].lower() if '.' in self.filename else ''

            # File size
            try:
                self.file_size = self.file.size
            except (OSError, AttributeError):
                pass

        # Auto-set year/month
        if not self.year or not self.month:
            if self.obligation:
                self.year = self.obligation.year
                self.month = self.obligation.month
            else:
                now = datetime.now()
                self.year = self.year or now.year
                self.month = self.month or now.month

        # Auto-set category from obligation type
        if self.obligation and self.document_category == 'general':
            self.document_category = self._get_category_from_obligation()

        # Ensure folders exist
        if self.client and not self.pk:  # Only on create
            self._ensure_folders_exist()

        super().save(*args, **kwargs)

    def _get_category_from_obligation(self):
        """Αυτόματη κατηγορία βάσει τύπου υποχρέωσης"""
        if not self.obligation or not self.obligation.obligation_type:
            return 'general'

        type_code = self.obligation.obligation_type.code.upper()

        category_map = {
            'ΦΠΑ': 'vat', 'VAT': 'vat', 'FPA': 'vat',
            'ΜΥΦ': 'myf', 'MYF': 'myf',
            'ΑΠΔ': 'apd', 'APD': 'apd',
            'ΕΦΚΑ': 'efka', 'EFKA': 'efka', 'IKA': 'efka',
            'Ε1': 'tax', 'Ε3': 'tax', 'E1': 'tax', 'E3': 'tax',
            'PAYROLL': 'payroll', 'ΜΙΣΘ': 'payroll',
        }

        for key, cat in category_map.items():
            if key in type_code:
                return cat
        return 'general'

    def _ensure_folders_exist(self):
        """Δημιουργία φακέλων αν δεν υπάρχουν"""
        try:
            client_path = os.path.join(
                settings.MEDIA_ROOT,
                get_client_folder(self.client)
            )
            year_path = os.path.join(client_path, str(self.year))
            month_path = os.path.join(year_path, f"{self.month:02d}")

            for category, _ in self.CATEGORY_CHOICES:
                os.makedirs(os.path.join(month_path, category), exist_ok=True)
        except Exception:
            pass  # Fail silently - Django will create on upload

    @classmethod
    def check_existing(cls, client, obligation=None, category=None):
        """
        Έλεγχος αν υπάρχει ήδη αρχείο για αυτόν τον συνδυασμό.
        Επιστρέφει το υπάρχον αρχείο ή None.
        """
        qs = cls.objects.filter(client=client, is_current=True)

        if obligation:
            qs = qs.filter(obligation=obligation)
        if category:
            qs = qs.filter(document_category=category)

        return qs.first()

    def create_new_version(self, new_file, user=None):
        """
        Δημιουργεί νέα έκδοση του εγγράφου.
        Το παλιό γίνεται is_current=False.

        Returns: new ClientDocument instance
        """
        # Mark this as not current
        self.is_current = False
        self.save(update_fields=['is_current'])

        # Create new version
        new_doc = ClientDocument(
            client=self.client,
            obligation=self.obligation,
            file=new_file,
            original_filename=os.path.basename(new_file.name),
            document_category=self.document_category,
            year=self.year,
            month=self.month,
            version=self.version + 1,
            is_current=True,
            previous_version=self,
            description=self.description,
            uploaded_by=user,
        )
        new_doc.save()
        return new_doc

    def get_all_versions(self):
        """Επιστρέφει όλες τις εκδόσεις (συμπεριλαμβανομένης αυτής)"""
        # Find the root
        root = self
        while root.previous_version:
            root = root.previous_version

        # Get all versions from root
        versions = [root]
        current = root
        while True:
            next_version = current.next_versions.first()
            if not next_version:
                break
            versions.append(next_version)
            current = next_version

        return versions

    @property
    def file_size_display(self):
        """Μέγεθος σε human-readable format"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def folder_path(self):
        """Επιστρέφει το path του φακέλου (χωρίς το filename)"""
        if self.file:
            return os.path.dirname(self.file.path)
        return None

    @property
    def full_path(self):
        """Επιστρέφει το πλήρες path του αρχείου"""
        if self.file:
            return self.file.path
        return None


# Signals for auto-folder creation
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ClientProfile)
def create_client_folders(sender, instance, created, **kwargs):
    """
    Auto-create folder structure για νέους πελάτες.

    Χρησιμοποιεί τις ρυθμίσεις από FilingSystemSettings για:
    - Τοποθεσία (local ή network)
    - Μόνιμο φάκελο (00_ΜΟΝΙΜΑ)
    - Κατηγορίες φακέλων
    """
    if not created:
        return

    # Λήψη ρυθμίσεων αρχειοθέτησης
    try:
        from settings.models import FilingSystemSettings
        filing_settings = FilingSystemSettings.get_settings()
        archive_root = filing_settings.get_archive_root()
    except Exception:
        archive_root = str(settings.MEDIA_ROOT)
        filing_settings = None

    base_path = os.path.join(archive_root, get_client_folder(instance))

    try:
        # === ΜΟΝΙΜΟΣ ΦΑΚΕΛΟΣ (00_ΜΟΝΙΜΑ) ===
        if filing_settings and filing_settings.enable_permanent_folder:
            permanent_path = os.path.join(base_path, filing_settings.permanent_folder_name)
            for category in filing_settings.get_permanent_folder_categories():
                os.makedirs(os.path.join(permanent_path, category), exist_ok=True)
        else:
            # Fallback - δημιουργία βασικών φακέλων
            for category in ['contracts', 'registration', 'licenses']:
                os.makedirs(os.path.join(base_path, '00_ΜΟΝΙΜΑ', category), exist_ok=True)

        # === ΤΡΕΧΟΝ ΕΤΟΣ ===
        current_year = datetime.now().year
        year_path = os.path.join(base_path, str(current_year))

        # Δημιουργία μηνιαίων φακέλων για τρέχον έτος
        monthly_categories = (
            filing_settings.get_monthly_folder_categories()
            if filing_settings else
            ['vat', 'apd', 'myf', 'payroll', 'invoices_issued', 'invoices_received', 'bank', 'general']
        )

        for month in range(1, 13):
            if filing_settings and filing_settings.use_greek_month_names:
                month_name = filing_settings.get_month_folder_name(month)
            else:
                month_name = f"{month:02d}"

            month_path = os.path.join(year_path, month_name)
            for category in monthly_categories:
                os.makedirs(os.path.join(month_path, category), exist_ok=True)

        # === ΕΤΗΣΙΟΣ ΦΑΚΕΛΟΣ (13_ΕΤΗΣΙΑ) ===
        if filing_settings and filing_settings.enable_yearend_folder:
            yearend_path = os.path.join(year_path, filing_settings.yearend_folder_name)
            for category in filing_settings.get_yearend_folder_categories():
                os.makedirs(os.path.join(yearend_path, category), exist_ok=True)
        else:
            # Fallback
            yearend_path = os.path.join(year_path, '13_ΕΤΗΣΙΑ')
            for category in ['e1', 'e2', 'e3', 'enfia', 'balance']:
                os.makedirs(os.path.join(yearend_path, category), exist_ok=True)

        # === INFO.txt ===
        readme_path = os.path.join(base_path, 'INFO.txt')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"ΦΑΚΕΛΟΣ ΠΕΛΑΤΗ\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Επωνυμία: {instance.eponimia}\n")
            f.write(f"ΑΦΜ: {instance.afm}\n")
            f.write(f"ΔΟΥ: {instance.doy or '-'}\n")
            f.write(f"Email: {instance.email or '-'}\n")
            f.write(f"Τηλέφωνο: {instance.phone or '-'}\n")
            f.write(f"\nΔημιουργία: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"\n{'=' * 50}\n")
            f.write(f"ΔΟΜΗ ΦΑΚΕΛΩΝ\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"00_ΜΟΝΙΜΑ/      → Μόνιμα έγγραφα (συμβάσεις, καταστατικό)\n")
            f.write(f"  ├─ registration/  → Ιδρυτικά έγγραφα\n")
            f.write(f"  ├─ contracts/     → Συμβάσεις\n")
            f.write(f"  └─ licenses/      → Άδειες & πιστοποιητικά\n\n")
            f.write(f"YYYY/           → Φάκελος έτους\n")
            f.write(f"  ├─ 01-12/         → Μηνιαίοι φάκελοι\n")
            f.write(f"  │   ├─ vat/           → ΦΠΑ\n")
            f.write(f"  │   ├─ apd/           → ΑΠΔ/ΕΦΚΑ\n")
            f.write(f"  │   ├─ myf/           → ΜΥΦ\n")
            f.write(f"  │   ├─ payroll/       → Μισθοδοσία\n")
            f.write(f"  │   ├─ invoices_issued/  → Εκδοθέντα τιμολόγια\n")
            f.write(f"  │   ├─ invoices_received/→ Ληφθέντα τιμολόγια\n")
            f.write(f"  │   ├─ bank/          → Τραπεζικά\n")
            f.write(f"  │   └─ general/       → Γενικά\n")
            f.write(f"  └─ 13_ΕΤΗΣΙΑ/     → Ετήσιες δηλώσεις\n")
            f.write(f"      ├─ e1/            → Ε1 Φόρος Εισοδήματος\n")
            f.write(f"      ├─ e2/            → Ε2 Ακίνητα\n")
            f.write(f"      ├─ e3/            → Ε3 Οικονομικά Στοιχεία\n")
            f.write(f"      ├─ enfia/         → ΕΝΦΙΑ\n")
            f.write(f"      └─ balance/       → Ισολογισμός\n")

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Could not create folders for client {instance.afm}: {e}")


# ============================================
# DOCUMENT TAGGING SYSTEM
# ============================================

class DocumentTag(models.Model):
    """
    Tags για κατηγοριοποίηση εγγράφων.
    Επιτρέπει custom labels πέρα από τις προκαθορισμένες κατηγορίες.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Όνομα'
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name='Χρώμα',
        help_text='Hex color code (π.χ. #3B82F6)'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Εικονίδιο',
        help_text='Lucide icon name (π.χ. file-text)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Περιγραφή'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_tags',
        verbose_name='Δημιουργήθηκε από'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ετικέτα Εγγράφου'
        verbose_name_plural = 'Ετικέτες Εγγράφων'

    def __str__(self):
        return self.name


class DocumentTagAssignment(models.Model):
    """
    Σύνδεση εγγράφων με tags (many-to-many through table).
    """
    document = models.ForeignKey(
        ClientDocument,
        on_delete=models.CASCADE,
        related_name='tag_assignments'
    )
    tag = models.ForeignKey(
        DocumentTag,
        on_delete=models.CASCADE,
        related_name='document_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tag_assignments'
    )

    class Meta:
        unique_together = ['document', 'tag']
        ordering = ['-assigned_at']
        verbose_name = 'Ανάθεση Ετικέτας'
        verbose_name_plural = 'Αναθέσεις Ετικετών'

    def __str__(self):
        return f"{self.document.filename} - {self.tag.name}"


# ============================================
# SHARED LINKS FOR FILE SHARING
# ============================================

import secrets
from django.utils import timezone

def generate_share_token():
    """Δημιουργεί unique token για shared link"""
    return secrets.token_urlsafe(32)


class SharedLink(models.Model):
    """
    Κοινόχρηστοι σύνδεσμοι για διαμοιρασμό εγγράφων.
    Υποστηρίζει expiration, password protection, και download limits.
    """
    ACCESS_LEVELS = [
        ('view', 'Μόνο προβολή'),
        ('download', 'Προβολή & Λήψη'),
    ]

    # Link target - μπορεί να είναι single document ή folder (client)
    document = models.ForeignKey(
        ClientDocument,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='shared_links',
        verbose_name='Έγγραφο'
    )
    client = models.ForeignKey(
        ClientProfile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='shared_folder_links',
        verbose_name='Φάκελος Πελάτη'
    )

    # Link settings
    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_share_token,
        verbose_name='Token'
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Όνομα Συνδέσμου',
        help_text='Φιλικό όνομα για αναγνώριση'
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVELS,
        default='download',
        verbose_name='Επίπεδο Πρόσβασης'
    )

    # Security
    password_hash = models.CharField(
        max_length=128,
        blank=True,
        verbose_name='Κωδικός (hashed)'
    )
    requires_email = models.BooleanField(
        default=False,
        verbose_name='Απαιτεί Email',
        help_text='Ο χρήστης πρέπει να εισάγει email για πρόσβαση'
    )

    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Λήξη',
        help_text='Αν είναι κενό, δεν λήγει'
    )
    max_downloads = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Μέγιστες Λήψεις',
        help_text='Αν είναι κενό, απεριόριστες'
    )

    # Statistics
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Πλήθος Λήψεων'
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Πλήθος Προβολών'
    )
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Τελευταία Πρόσβαση'
    )

    # Audit
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ενεργό'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_shared_links',
        verbose_name='Δημιουργήθηκε από'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Κοινόχρηστος Σύνδεσμος'
        verbose_name_plural = 'Κοινόχρηστοι Σύνδεσμοι'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['is_active', 'expires_at']),
        ]

    def __str__(self):
        target = self.document.filename if self.document else f"Φάκελος: {self.client.eponimia}"
        return f"{self.name or target} ({self.token[:8]}...)"

    def save(self, *args, **kwargs):
        if not self.name:
            if self.document:
                self.name = self.document.filename
            elif self.client:
                self.name = f"Φάκελος: {self.client.eponimia}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Έλεγχος αν έχει λήξει"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_download_limit_reached(self):
        """Έλεγχος αν έχει φτάσει το όριο λήψεων"""
        if not self.max_downloads:
            return False
        return self.download_count >= self.max_downloads

    @property
    def is_valid(self):
        """Συνολικός έλεγχος εγκυρότητας"""
        return (
            self.is_active and
            not self.is_expired and
            not self.is_download_limit_reached
        )

    def set_password(self, password):
        """Ορισμός κωδικού (hashed)"""
        from django.contrib.auth.hashers import make_password
        self.password_hash = make_password(password)

    def check_password(self, password):
        """Έλεγχος κωδικού"""
        if not self.password_hash:
            return True
        from django.contrib.auth.hashers import check_password
        return check_password(password, self.password_hash)

    def record_access(self, is_download=False):
        """Καταγραφή πρόσβασης"""
        self.last_accessed_at = timezone.now()
        self.view_count += 1
        if is_download:
            self.download_count += 1
        self.save(update_fields=['last_accessed_at', 'view_count', 'download_count'])

    def get_public_url(self):
        """Δημιουργία public URL"""
        from django.urls import reverse
        return reverse('accounting:shared_link_access', args=[self.token])


class SharedLinkAccess(models.Model):
    """
    Καταγραφή προσβάσεων σε shared links (audit log).
    """
    shared_link = models.ForeignKey(
        SharedLink,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Διεύθυνση'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    email_provided = models.EmailField(
        blank=True,
        verbose_name='Email που δόθηκε'
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('view', 'Προβολή'),
            ('download', 'Λήψη'),
        ],
        default='view',
        verbose_name='Ενέργεια'
    )

    class Meta:
        ordering = ['-accessed_at']
        verbose_name = 'Πρόσβαση Συνδέσμου'
        verbose_name_plural = 'Προσβάσεις Συνδέσμων'

    def __str__(self):
        return f"{self.shared_link} - {self.action} - {self.accessed_at}"


# ============================================
# DOCUMENT FAVORITES
# ============================================

class DocumentFavorite(models.Model):
    """
    Αγαπημένα έγγραφα ανά χρήστη.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_documents'
    )
    document = models.ForeignKey(
        ClientDocument,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Σημείωση'
    )

    class Meta:
        unique_together = ['user', 'document']
        ordering = ['-created_at']
        verbose_name = 'Αγαπημένο Έγγραφο'
        verbose_name_plural = 'Αγαπημένα Έγγραφα'

    def __str__(self):
        return f"{self.user.username} - {self.document.filename}"


# ============================================
# DOCUMENT COLLECTIONS (FOLDERS)
# ============================================

class DocumentCollection(models.Model):
    """
    Virtual folders/collections για οργάνωση εγγράφων.
    Επιτρέπει στους χρήστες να δημιουργούν custom συλλογές.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Όνομα'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Περιγραφή'
    )
    color = models.CharField(
        max_length=7,
        default='#6366F1',
        verbose_name='Χρώμα'
    )
    icon = models.CharField(
        max_length=50,
        default='folder',
        verbose_name='Εικονίδιο'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_collections',
        verbose_name='Ιδιοκτήτης'
    )
    is_shared = models.BooleanField(
        default=False,
        verbose_name='Κοινόχρηστο',
        help_text='Ορατό σε όλους τους χρήστες'
    )
    documents = models.ManyToManyField(
        ClientDocument,
        blank=True,
        related_name='collections',
        verbose_name='Έγγραφα'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Συλλογή Εγγράφων'
        verbose_name_plural = 'Συλλογές Εγγράφων'

    def __str__(self):
        return f"{self.name} ({self.documents.count()} έγγραφα)"

    @property
    def document_count(self):
        return self.documents.count()