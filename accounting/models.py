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
    
    profile = models.ForeignKey(ObligationProfile, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Profile Υποχρεώσεων',
                               related_name='obligations',
                               help_text='Αν ανήκει σε profile (π.χ. Μισθοδοσία)')
    
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
        
        if self.frequency in ['quarterly', 'annual'] and self.applicable_months:
            applicable = [int(m) for m in self.applicable_months.split(',')]
            return month in applicable
        
        return False


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
            obligations.update(profile.obligations.all())
        
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
    Pattern: clients/{ΑΦΜ}_{Επωνυμία}/{YYYY}/{MM}/{category}/{filename}

    Αν υπάρχει obligation, χρησιμοποιεί το year/month της υποχρέωσης.
    Αλλιώς χρησιμοποιεί την τρέχουσα ημερομηνία.
    """
    client_folder = get_client_folder(instance.client)
    category = instance.document_category if instance.document_category else 'general'

    # Χρήση year/month από obligation αν υπάρχει, αλλιώς τρέχουσα ημερομηνία
    if instance.obligation:
        year = str(instance.obligation.year)
        month = f"{instance.obligation.month:02d}"
    else:
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}"

    return os.path.join(client_folder, year, month, category, filename)


class ClientDocument(models.Model):
    """
    Ενιαίο model για όλα τα έγγραφα πελατών.

    Χρησιμοποιείται τόσο για γενικά έγγραφα όσο και για
    συνημμένα υποχρεώσεων. Υποστηρίζει versioning.
    """

    CATEGORY_CHOICES = [
        ('contracts', 'Συμβάσεις'),
        ('invoices', 'Τιμολόγια'),
        ('tax', 'Φορολογικά'),
        ('myf', 'ΜΥΦ'),
        ('vat', 'ΦΠΑ'),
        ('apd', 'ΑΠΔ'),
        ('payroll', 'Μισθοδοσία'),
        ('efka', 'ΕΦΚΑ'),
        ('general', 'Γενικά'),
    ]

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
    """Auto-create folder structure για νέους πελάτες"""
    if created:
        base_path = os.path.join(settings.MEDIA_ROOT, get_client_folder(instance))
        
        # Δημιουργία καταλόγων
        categories = ['contracts', 'invoices', 'tax', 'myf', 'vat', 'payroll', 'general']
        for category in categories:
            os.makedirs(os.path.join(base_path, category), exist_ok=True)
        
        # README file
        readme_path = os.path.join(base_path, 'INFO.txt')
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"ΦΑΚΕΛΟΣ ΠΕΛΑΤΗ\n")
                f.write(f"{'='*40}\n")
                f.write(f"Επωνυμία: {instance.eponimia}\n")
                f.write(f"ΑΦΜ: {instance.afm}\n")
                f.write(f"ΔΟΥ: {instance.doy}\n")
                f.write(f"Δημιουργία: {datetime.now().strftime('%d/%m/%Y')}\n")
        except Exception as e:
            print(f"Could not create INFO.txt: {e}")