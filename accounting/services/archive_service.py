"""
Κεντρική υπηρεσία αρχειοθέτησης για LogistikoCRM.

Αντικαθιστά τη διάσπαρτη λογική path generation και file management,
παρέχοντας μία πηγή αλήθειας για όλες τις λειτουργίες αρχειοθέτησης.

Author: LogistikoCRM Team
Date: December 2025
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from common.utils.file_validation import validate_file_upload

logger = logging.getLogger(__name__)


class ArchiveService:
    """
    Κεντρική υπηρεσία για διαχείριση αρχείων.

    Παρέχει:
    - Ενοποιημένη path generation
    - File validation με context awareness
    - Duplicate detection και handling
    - Consistent error messages (Ελληνικά)
    """

    # =========================================================================
    # PATH GENERATION - ΜΟΝΑΔΙΚΗ ΠΗΓΗ ΑΛΗΘΕΙΑΣ
    # =========================================================================

    @staticmethod
    def get_safe_client_name(client) -> str:
        """
        Δημιουργεί ασφαλές όνομα φακέλου για πελάτη.

        Format: "{afm}_{sanitized_name}"
        - Αφαιρεί ειδικούς χαρακτήρες
        - Αντικαθιστά κενά με underscore
        - Μέγιστο 50 χαρακτήρες

        Args:
            client: ClientProfile instance

        Returns:
            str: Safe folder name (e.g., "123456789_ACME_SA")

        Examples:
            >>> client.afm = "123456789"
            >>> client.eponimia = "ACME Α.Ε. & ΣΙΑ"
            >>> get_safe_client_name(client)
            "123456789_ACME__"
        """
        # Sanitize name: remove special chars, keep alphanumeric + spaces + hyphens
        safe_name = re.sub(r'[^\w\s-]', '', client.eponimia)[:30]

        # Replace spaces and slashes with underscores
        safe_name = safe_name.replace(' ', '_').replace('/', '_')

        # Remove multiple consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)

        # Combine AFM + name
        return f"{client.afm}_{safe_name}"

    @staticmethod
    def get_client_root(client) -> str:
        """
        Επιστρέφει το root directory path του πελάτη.

        Args:
            client: ClientProfile instance

        Returns:
            str: "clients/{safe_name}/"

        Examples:
            >>> get_client_root(client)
            "clients/123456789_ACME_SA"
        """
        return f"clients/{ArchiveService.get_safe_client_name(client)}"

    @staticmethod
    def get_obligation_path(client, obligation_type_code: str, year: int, month: int) -> str:
        """
        Δημιουργεί το standardized path για υποχρέωση.

        Format: clients/{afm}_{name}/{year}/{month:02d}/{type_code}/

        Args:
            client: ClientProfile instance
            obligation_type_code: Κωδικός υποχρέωσης (ΦΠΑ, ΑΠΔ, κλπ)
            year: Έτος
            month: Μήνας (1-12)

        Returns:
            str: Folder path without filename
        """
        client_root = ArchiveService.get_client_root(client)
        return f"{client_root}/{year}/{month:02d}/{obligation_type_code}"

    @staticmethod
    def get_document_path(client, category: str, year: Optional[int] = None,
                         month: Optional[int] = None) -> str:
        """
        Δημιουργεί path για ClientDocument.

        Format: clients/{afm}_{name}/{category}/{year}/{month}/

        Args:
            client: ClientProfile instance
            category: Document category (contracts, invoices, tax, etc.)
            year: Optional year (defaults to current)
            month: Optional month (defaults to current)

        Returns:
            str: Folder path without filename
        """
        now = datetime.now()
        year = year or now.year
        month = month or now.month

        client_root = ArchiveService.get_client_root(client)
        return f"{client_root}/{category}/{year}/{month:02d}"

    # =========================================================================
    # FILE VALIDATION
    # =========================================================================

    @staticmethod
    def validate_file(uploaded_file, context: str = 'document') -> Tuple[bool, Optional[str]]:
        """
        Επικυρώνει αρχείο με βάση το context.

        Contexts:
        - 'obligation': Μόνο PDF, max 10MB
        - 'document': Όλοι οι τύποι, max 25MB
        - 'image': Μόνο εικόνες, max 10MB

        Args:
            uploaded_file: Django UploadedFile
            context: Validation context

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)

        Examples:
            >>> is_valid, error = validate_file(file, 'obligation')
            >>> if not is_valid:
            ...     print(error)
        """
        if not uploaded_file:
            return False, "Δεν παρέχεται αρχείο"

        # Get file extension
        filename = uploaded_file.name
        ext = os.path.splitext(filename)[1].lower()

        # Context-specific validation
        if context == 'obligation':
            # MonthlyObligation: PDF only, max 10MB
            if ext != '.pdf':
                return False, "Επιτρέπονται μόνο αρχεία PDF για υποχρεώσεις"

            max_size = 10 * 1024 * 1024  # 10MB
            if uploaded_file.size > max_size:
                size_mb = uploaded_file.size / (1024 * 1024)
                return False, f"Το αρχείο υπερβαίνει τα 10MB (μέγεθος: {size_mb:.1f}MB)"

        elif context == 'document':
            # ClientDocument: All office formats + images, max 25MB
            try:
                validate_file_upload(uploaded_file)
            except ValidationError as e:
                return False, str(e)

            max_size = 25 * 1024 * 1024  # 25MB
            if uploaded_file.size > max_size:
                size_mb = uploaded_file.size / (1024 * 1024)
                return False, f"Το αρχείο υπερβαίνει τα 25MB (μέγεθος: {size_mb:.1f}MB)"

        elif context == 'image':
            # Images only
            if ext not in {'.jpg', '.jpeg', '.png', '.gif'}:
                return False, "Επιτρέπονται μόνο εικόνες (JPG, PNG, GIF)"

            max_size = 10 * 1024 * 1024  # 10MB
            if uploaded_file.size > max_size:
                return False, "Η εικόνα υπερβαίνει τα 10MB"

        else:
            # Unknown context - use general validation
            try:
                validate_file_upload(uploaded_file)
            except ValidationError as e:
                return False, str(e)

        return True, None

    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================

    @staticmethod
    def file_exists(path: str) -> bool:
        """
        Ελέγχει αν υπάρχει αρχείο.

        Args:
            path: Relative path to file

        Returns:
            bool: True if exists
        """
        return default_storage.exists(path)

    @staticmethod
    def get_file_info(path: str) -> Dict:
        """
        Επιστρέφει metadata για υπάρχον αρχείο.

        Args:
            path: Relative path to file

        Returns:
            Dict with: path, name, size, modified, exists
        """
        if not default_storage.exists(path):
            return {
                'path': path,
                'name': os.path.basename(path),
                'exists': False
            }

        try:
            return {
                'path': path,
                'name': os.path.basename(path),
                'size': default_storage.size(path),
                'modified': default_storage.get_modified_time(path),
                'exists': True
            }
        except Exception as e:
            logger.warning(f"Could not get file info for {path}: {e}")
            return {
                'path': path,
                'name': os.path.basename(path),
                'exists': True,
                'error': str(e)
            }

    @staticmethod
    def get_versioned_path(filepath: str) -> str:
        """
        Δημιουργεί versioned path για duplicates.

        Strategy: file.pdf → file_v2.pdf → file_v3.pdf

        Args:
            filepath: Original path

        Returns:
            str: Next available versioned path

        Examples:
            >>> get_versioned_path("clients/123/file.pdf")
            "clients/123/file_v2.pdf"
        """
        base, ext = os.path.splitext(filepath)
        version = 2

        while default_storage.exists(f"{base}_v{version}{ext}"):
            version += 1

        return f"{base}_v{version}{ext}"

    @staticmethod
    def save_file(uploaded_file, target_path: str, on_duplicate: str = 'ask') -> Dict:
        """
        Αποθηκεύει αρχείο με έλεγχο duplicates.

        Args:
            uploaded_file: Django UploadedFile
            target_path: Relative path (e.g., "clients/123_ACME/2025/01/ΦΠΑ/file.pdf")
            on_duplicate: 'ask' | 'replace' | 'keep_both'
                - 'ask': Return duplicate info for user decision
                - 'replace': Delete existing, save new
                - 'keep_both': Add version suffix (_v2, _v3, etc.)

        Returns:
            Dict:
                Success: {
                    'success': True,
                    'path': str,
                    'action': 'created'|'replaced'|'versioned',
                    'size': int
                }
                Duplicate (ask): {
                    'success': False,
                    'requires_decision': True,
                    'existing_file': {...},
                    'suggested_path': str
                }
                Error: {
                    'success': False,
                    'error': str
                }
        """
        try:
            # Check if file exists
            file_exists = default_storage.exists(target_path)
            action = 'created'

            if file_exists:
                if on_duplicate == 'ask':
                    # Return info for user decision
                    existing_info = ArchiveService.get_file_info(target_path)
                    return {
                        'success': False,
                        'requires_decision': True,
                        'existing_file': existing_info,
                        'suggested_path': ArchiveService.get_versioned_path(target_path),
                        'new_file': {
                            'name': uploaded_file.name,
                            'size': uploaded_file.size
                        }
                    }

                elif on_duplicate == 'replace':
                    # Delete existing file
                    logger.info(f"[ARCHIVE] Replacing existing file: {target_path}")
                    default_storage.delete(target_path)
                    action = 'replaced'

                elif on_duplicate == 'keep_both':
                    # Create versioned filename
                    original_path = target_path
                    target_path = ArchiveService.get_versioned_path(target_path)
                    logger.info(f"[ARCHIVE] Versioning: {original_path} → {target_path}")
                    action = 'versioned'

            # Read file content
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            uploaded_file.seek(0)

            # Save using Django storage
            saved_path = default_storage.save(target_path, ContentFile(file_content))

            logger.info(f"[ARCHIVE] File saved: {saved_path} ({action})")

            return {
                'success': True,
                'path': saved_path,
                'action': action,
                'size': uploaded_file.size,
                'name': os.path.basename(saved_path)
            }

        except Exception as e:
            logger.error(f"[ARCHIVE] Error saving file: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Σφάλμα αποθήκευσης αρχείου: {str(e)}"
            }

    @staticmethod
    def validate_and_save(uploaded_file, target_path: str,
                         context: str = 'document',
                         on_duplicate: str = 'ask') -> Dict:
        """
        Ολοκληρωμένη διαδικασία: Validation + Save.

        Χρησιμοποίησε αυτό για consistent behavior σε όλο το project.

        Args:
            uploaded_file: Django UploadedFile
            target_path: Where to save
            context: 'obligation' | 'document' | 'image'
            on_duplicate: 'ask' | 'replace' | 'keep_both'

        Returns:
            Dict: Same as save_file(), plus validation errors
        """
        # Step 1: Validate
        is_valid, error = ArchiveService.validate_file(uploaded_file, context)

        if not is_valid:
            logger.warning(f"[ARCHIVE] Validation failed: {error}")
            return {
                'success': False,
                'error': error
            }

        # Step 2: Save
        return ArchiveService.save_file(uploaded_file, target_path, on_duplicate)

    # =========================================================================
    # HIGH-LEVEL HELPERS
    # =========================================================================

    @staticmethod
    def process_obligation_upload(obligation, uploaded_file,
                                  on_duplicate: str = 'ask',
                                  description: str = '') -> Dict:
        """
        ΚΕΝΤΡΙΚΟ ENTRY POINT για obligation file uploads.

        Χρησιμοποίησε αυτό σε όλα τα upload points (admin, views, API).

        Handles:
        - Validation (PDF only, 10MB)
        - Path generation via ArchiveConfiguration
        - Duplicate detection
        - Save to storage
        - Update MonthlyObligation.attachment field

        Args:
            obligation: MonthlyObligation instance
            uploaded_file: Django UploadedFile
            on_duplicate: 'ask' | 'replace' | 'keep_both'
            description: Optional description for the file

        Returns:
            Dict: Result from validate_and_save()

        Note:
            This method does NOT handle JSONField attachments - that's done
            by obligation.add_attachment() for multi-file support.
        """
        # Get ArchiveConfiguration
        from accounting.models import ArchiveConfiguration

        config, _ = ArchiveConfiguration.objects.get_or_create(
            obligation_type=obligation.obligation_type,
            defaults={
                'filename_pattern': '{type_code}_{month}_{year}.pdf',
                'folder_pattern': 'clients/{client_afm}_{client_name}/{year}/{month}/{type_code}/',
            }
        )

        # Generate target path
        target_path = config.get_archive_path(obligation, uploaded_file.name)

        logger.info(f"[ARCHIVE] Processing obligation upload: {obligation} → {target_path}")

        # Validate and save
        result = ArchiveService.validate_and_save(
            uploaded_file,
            target_path,
            context='obligation',
            on_duplicate=on_duplicate
        )

        # If successful, update obligation.attachment field
        if result.get('success'):
            obligation.attachment.name = result['path']
            obligation.save(update_fields=['attachment'])
            logger.info(f"[ARCHIVE] Updated obligation.attachment: {result['path']}")

        return result


# =============================================================================
# BACKWARDS COMPATIBILITY HELPERS
# =============================================================================

def get_safe_client_name(client):
    """
    DEPRECATED: Use ArchiveService.get_safe_client_name()

    Kept for backwards compatibility with existing code.
    """
    return ArchiveService.get_safe_client_name(client)


def get_client_folder(client):
    """
    DEPRECATED: Use ArchiveService.get_client_root()

    Kept for backwards compatibility with existing code.
    """
    return ArchiveService.get_client_root(client)
