from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os


class BackupSettings(models.Model):
    """
    Ρυθμίσεις Backup - Singleton model.
    """

    class Meta:
        verbose_name = _('Ρυθμίσεις Backup')
        verbose_name_plural = _('Ρυθμίσεις Backup')
        permissions = [
            ('can_create_backup', 'Δημιουργία backup'),
            ('can_restore_backup', 'Επαναφορά backup'),
            ('can_download_backup', 'Λήψη backup'),
        ]

    backup_path = models.CharField(
        'Φάκελος Backup',
        max_length=500,
        default='backups/',
        help_text='Σχετικό path από το MEDIA_ROOT ή απόλυτο path'
    )
    include_media = models.BooleanField(
        'Συμπερίληψη Media',
        default=True,
        help_text='Να συμπεριλαμβάνονται τα uploaded αρχεία'
    )
    max_backups = models.PositiveIntegerField(
        'Μέγιστος αριθμός Backups',
        default=10,
        help_text='Αυτόματη διαγραφή παλαιότερων (0 = χωρίς όριο)'
    )
    created_at = models.DateTimeField('Δημιουργήθηκε', auto_now_add=True)
    updated_at = models.DateTimeField('Ενημερώθηκε', auto_now=True)

    def save(self, *args, **kwargs):
        # Singleton pattern
        if not self.pk and BackupSettings.objects.exists():
            existing = BackupSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Επιστρέφει τις ρυθμίσεις ή δημιουργεί default."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_backup_dir(self):
        """Επιστρέφει το πλήρες path του backup folder."""
        if os.path.isabs(self.backup_path):
            return self.backup_path
        return os.path.join(settings.MEDIA_ROOT, self.backup_path)

    def __str__(self):
        return f"Backup Settings ({self.backup_path})"


class BackupHistory(models.Model):
    """
    Ιστορικό Backups.
    """

    class Meta:
        verbose_name = _('Backup')
        verbose_name_plural = _('Ιστορικό Backups')
        ordering = ['-created_at']

    RESTORE_MODE_CHOICES = [
        ('replace', 'Αντικατάσταση'),
        ('merge', 'Συγχώνευση'),
    ]

    filename = models.CharField('Αρχείο', max_length=255)
    file_path = models.CharField('Πλήρες Path', max_length=500)
    file_size = models.BigIntegerField('Μέγεθος (bytes)', default=0)
    includes_db = models.BooleanField('Περιέχει DB', default=True)
    includes_media = models.BooleanField('Περιέχει Media', default=False)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backups_created',
        verbose_name='Δημιουργήθηκε από'
    )
    created_at = models.DateTimeField('Δημιουργήθηκε', auto_now_add=True)
    notes = models.TextField('Σημειώσεις', blank=True)

    # Restore tracking
    restored_at = models.DateTimeField('Επαναφέρθηκε', null=True, blank=True)
    restored_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backups_restored',
        verbose_name='Επαναφέρθηκε από'
    )
    restore_mode = models.CharField(
        'Τρόπος επαναφοράς',
        max_length=10,
        choices=RESTORE_MODE_CHOICES,
        null=True,
        blank=True
    )

    def file_size_display(self):
        """Εμφάνιση μεγέθους σε human-readable format."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def file_exists(self):
        """Έλεγχος αν το αρχείο υπάρχει."""
        return os.path.exists(self.file_path)

    def __str__(self):
        return f"{self.filename} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


class GSISSettings(models.Model):
    """
    Ρυθμίσεις για GSIS API (Λήψη στοιχείων με ΑΦΜ).

    Χρησιμοποιεί τους "Ειδικούς Κωδικούς Λήψης Στοιχείων" της ΑΑΔΕ.
    Singleton model - μόνο μία εγγραφή επιτρέπεται.
    """

    class Meta:
        verbose_name = _('Ρυθμίσεις GSIS')
        verbose_name_plural = _('Ρυθμίσεις GSIS')

    afm = models.CharField(
        'ΑΦΜ',
        max_length=9,
        help_text='Το ΑΦΜ του λογιστή (για την παράμετρο afm_called_by)'
    )
    username = models.CharField(
        'Όνομα Χρήστη',
        max_length=100,
        help_text='Ειδικός κωδικός λήψης στοιχείων - Username'
    )
    password = models.CharField(
        'Κωδικός',
        max_length=100,
        help_text='Ειδικός κωδικός λήψης στοιχείων - Password'
    )
    is_active = models.BooleanField(
        'Ενεργό',
        default=True,
        help_text='Αν είναι απενεργοποιημένο, η λήψη στοιχείων δεν θα είναι διαθέσιμη'
    )
    created_at = models.DateTimeField('Δημιουργήθηκε', auto_now_add=True)
    updated_at = models.DateTimeField('Ενημερώθηκε', auto_now=True)

    def save(self, *args, **kwargs):
        # Singleton pattern - only one instance allowed
        if not self.pk and GSISSettings.objects.exists():
            # Update existing instead of creating new
            existing = GSISSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Επιστρέφει τις ρυθμίσεις GSIS ή None αν δεν υπάρχουν."""
        return cls.objects.first()

    def __str__(self):
        return f"GSIS Settings ({self.username})"


class BannedCompanyName(models.Model):
    """
    Model representing a banned company name.

    This model is used to store company names that block the automatic generation
    of commercial requests from spam messages.
    Each name is unique and cannot be null or blank.

    Attributes:
        name (str): The name of the banned company, stored as a unique string
            with a maximum length of 50 characters.
    """
    class Meta:
        verbose_name = _("Banned company name")
        verbose_name_plural = _("Banned company names")

    name = models.CharField(
        max_length=50, unique=True,
        null=False, blank=False,
        verbose_name=_("Name")
    )

    def __str__(self):
        """
        Returns the string representation of the banned company name.
        """
        return self.name


class MassmailSettings(models.Model):
    """
    Model for mass mailing settings.
    """

    class Meta:
        verbose_name = _("Massmail Settings")
        verbose_name_plural = _("Massmail Settings")

    emails_per_day = models.PositiveIntegerField(
        default=94,
        help_text="Daily message limit for email accounts."
    )
    use_business_time = models.BooleanField(
        default=False,
        help_text="Send only during business hours."
    )
    business_time_start = models.TimeField(
        default="08:30",
        help_text="Start of working hours."
    )
    business_time_end = models.TimeField(
        default="17:30",
        help_text="End of working hours."
    )
    unsubscribe_url = models.URLField(
        default="https://www.example.com/unsubscribe",
        help_text='"Unsubscribed successfully" page."'
    )

    def __str__(self):
        return "Settings"


class PublicEmailDomain(models.Model):
    """
    Model representing a public email domain list.

    This model is used to store public domains to identify them in messages
    and prevent company identification by email domain.
    Each domain is unique and stored in the lowercase.

    Attributes:
        domain (str): The email domain, stored as a unique string with a
            maximum length of 20 characters.
    """
    class Meta:
        verbose_name = _('Public email domain')
        verbose_name_plural = _('Public email domains')

    domain = models.CharField(
        max_length=20, unique=True,
        null=False, blank=False,
        verbose_name=_("Domain")
    )

    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure the domain is stored in lowercase.
        """
        self.domain = self.domain.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns the string representation of the public email domain.
        """
        return self.domain


class Reminders(models.Model):
    """
    Model for storing reminder settings.

    This model is used to configure the interval at which reminders are checked.

    Attributes:
        check_interval (int): The interval in seconds to check for reminders,
            stored as a positive integer. Defaults to 300 seconds.
    """
    class Meta:
        verbose_name = _('Reminder settings')
        verbose_name_plural = _('Reminder settings')

    check_interval = models.PositiveBigIntegerField(
        null=False, blank=False,
        default='300',
        verbose_name=_("Check interval"),
        help_text=_(
            "Specify the interval in seconds to check if it's time for a reminder."
        )
    )

    def __str__(self):
        """
        Returns a string representation of the reminder settings.
        """
        return "Settings"


class StopPhrase(models.Model):
    """
    Model representing a stop phrase.

    This model is used to store phrases that block the automatic generation
    of commercial requests from spam messages. It also tracks the last
    occurrence date of each phrase.

    Attributes:
        phrase (str): The stop phrase, stored as a unique string with a
            maximum length of 100 characters.
        last_occurrence_date (date): The date when the phrase was most recently
            encountered, updated automatically whenever the record is saved.
    """
    class Meta:
        verbose_name = _('Stop Phrase')
        verbose_name_plural = _('Stop Phrases')

    phrase = models.CharField(
        max_length=100, unique=True,
        null=False, blank=False,
        verbose_name=_("Phrase")
    )
    last_occurrence_date = models.DateField(
        auto_now=True,
        verbose_name=_("Last occurrence date"),
        help_text=_("Date of last occurrence of the phrase")
    )

    def hit(self):
        """
        Updates the last occurrence date of the stop phrase to the current date.
        """
        self.save()

    def __str__(self):
        """
        Returns the string representation of the stop phrase.
        """
        return self.phrase
