# mydata/encryption.py
"""
Encryption utilities για myDATA credentials.

Χρησιμοποιεί Fernet (symmetric encryption) από το cryptography package.
Το encryption key αποθηκεύεται στο Django SECRET_KEY.

SECURITY NOTES:
- Τα credentials κρυπτογραφούνται πριν αποθηκευτούν στη βάση
- Το SECRET_KEY ΠΡΕΠΕΙ να είναι ασφαλές και να μην αλλάζει
- Αν αλλάξει το SECRET_KEY, τα encrypted credentials θα χαθούν
"""

import base64
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_fernet_key() -> bytes:
    """
    Δημιουργεί ένα valid Fernet key από το Django SECRET_KEY.

    Fernet απαιτεί 32-byte URL-safe base64-encoded key.
    Χρησιμοποιούμε SHA-256 hash του SECRET_KEY για consistency.
    """
    secret = settings.SECRET_KEY.encode('utf-8')
    # SHA-256 produces 32 bytes
    key_hash = hashlib.sha256(secret).digest()
    # Fernet needs URL-safe base64
    return base64.urlsafe_b64encode(key_hash)


def _get_fernet() -> Fernet:
    """Get Fernet instance με το derived key."""
    return Fernet(_get_fernet_key())


def encrypt_value(plain_text: str) -> str:
    """
    Κρυπτογραφεί ένα string value.

    Args:
        plain_text: Το κείμενο προς κρυπτογράφηση

    Returns:
        Base64-encoded encrypted string

    Raises:
        ValueError: Αν το plain_text είναι κενό
    """
    if not plain_text:
        raise ValueError("Cannot encrypt empty value")

    try:
        fernet = _get_fernet()
        encrypted = fernet.encrypt(plain_text.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise


def decrypt_value(encrypted_text: str) -> str:
    """
    Αποκρυπτογραφεί ένα encrypted string.

    Args:
        encrypted_text: Base64-encoded encrypted string

    Returns:
        Decrypted plain text

    Raises:
        ValueError: Αν αποτύχει η αποκρυπτογράφηση
    """
    if not encrypted_text:
        raise ValueError("Cannot decrypt empty value")

    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(encrypted_text.encode('utf-8'))
        return decrypted.decode('utf-8')
    except InvalidToken:
        logger.error("Decryption failed - invalid token (possibly wrong SECRET_KEY)")
        raise ValueError(
            "Αποτυχία αποκρυπτογράφησης. "
            "Πιθανή αλλαγή SECRET_KEY ή κατεστραμμένα δεδομένα."
        )
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise


def is_encrypted(value: str) -> bool:
    """
    Ελέγχει αν ένα value είναι ήδη encrypted.

    Fernet encrypted strings έχουν συγκεκριμένο format:
    - Ξεκινούν με 'gAAAAA'
    - Είναι base64-encoded
    """
    if not value:
        return False

    # Fernet tokens start with version byte 0x80 which is 'gA' in base64
    return value.startswith('gAAAAA')


def safe_decrypt(encrypted_text: Optional[str]) -> Optional[str]:
    """
    Safe version of decrypt - returns None on error instead of raising.

    Χρήσιμο για cases όπου θέλουμε graceful degradation.
    """
    if not encrypted_text:
        return None

    try:
        return decrypt_value(encrypted_text)
    except Exception as e:
        logger.warning(f"Safe decrypt failed: {e}")
        return None


class EncryptedFieldMixin:
    """
    Mixin για encrypted model fields.

    Usage in models:
        class MyModel(EncryptedFieldMixin, models.Model):
            _encrypted_field = models.TextField()

            @property
            def field(self):
                return self.get_decrypted('_encrypted_field')

            @field.setter
            def field(self, value):
                self.set_encrypted('_encrypted_field', value)
    """

    def get_decrypted(self, field_name: str) -> Optional[str]:
        """Get decrypted value of an encrypted field."""
        encrypted = getattr(self, field_name, None)
        if not encrypted:
            return None
        return safe_decrypt(encrypted)

    def set_encrypted(self, field_name: str, plain_value: str):
        """Set encrypted value for a field."""
        if plain_value:
            setattr(self, field_name, encrypt_value(plain_value))
        else:
            setattr(self, field_name, '')
