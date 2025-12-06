# -*- coding: utf-8 -*-
"""
accounting/gsis_client.py
Author: Claude
Description: GSIS API Client για αναζήτηση στοιχείων με ΑΦΜ.

Χρησιμοποιεί το SOAP Web Service RgWsPublic2 της ΑΑΔΕ:
https://www1.gsis.gr/wsaade/RgWsPublic2/RgWsPublic2

Απαιτεί "Ειδικούς Κωδικούς Λήψης Στοιχείων" από την ΑΑΔΕ.
"""

import logging
import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


# GSIS SOAP Endpoint
GSIS_WSDL_URL = "https://www1.gsis.gr/wsaade/RgWsPublic2/RgWsPublic2"

# XML Namespaces
NAMESPACES = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'soap12': 'http://www.w3.org/2003/05/soap-envelope',
    'env': 'http://www.w3.org/2003/05/soap-envelope',
    'rgws': 'http://gr/gsis/rgwspublic2/RgWsPublic2',
    'ns2': 'http://gr/gsis/rgwspublic2/RgWsPublic2',
    'rg': 'http://gr/gsis/rgwspublic2/RgWsPublic2Service',
}


@dataclass
class AFMInfo:
    """Αποτέλεσμα αναζήτησης ΑΦΜ από GSIS."""
    afm: str
    doy: str
    doy_descr: str
    onomasia: str  # Επωνυμία
    legal_form: str  # Νομική μορφή
    legal_form_descr: str
    deactivation_flag: bool  # Απενεργοποιημένο
    deactivation_flag_descr: str
    firm_flag: bool  # Είναι επιχείρηση
    firm_flag_descr: str
    registration_date: Optional[str]  # Ημ/νία έναρξης
    stop_date: Optional[str]  # Ημ/νία διακοπής

    # Διεύθυνση έδρας
    postal_address: str
    postal_address_no: str
    postal_zip_code: str
    postal_area: str

    # Δραστηριότητες
    activities: List[Dict[str, Any]]

    # Raw data
    raw_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Επιστρέφει τα δεδομένα ως dictionary."""
        return {
            'afm': self.afm,
            'doy': self.doy,
            'doy_descr': self.doy_descr,
            'onomasia': self.onomasia,
            'legal_form': self.legal_form,
            'legal_form_descr': self.legal_form_descr,
            'deactivation_flag': self.deactivation_flag,
            'deactivation_flag_descr': self.deactivation_flag_descr,
            'firm_flag': self.firm_flag,
            'firm_flag_descr': self.firm_flag_descr,
            'registration_date': self.registration_date,
            'stop_date': self.stop_date,
            'postal_address': self.postal_address,
            'postal_address_no': self.postal_address_no,
            'postal_zip_code': self.postal_zip_code,
            'postal_area': self.postal_area,
            'activities': self.activities,
        }


class GSISError(Exception):
    """Exception για σφάλματα GSIS API."""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class GSISClient:
    """
    Client για το GSIS Web Service RgWsPublic2.

    Χρήση:
        client = GSISClient(afm='123456789', username='...', password='...')
        info = client.lookup_afm('987654321')
    """

    def __init__(self, afm: str, username: str, password: str):
        """
        Αρχικοποίηση του client.

        Args:
            afm: ΑΦΜ του λογιστή (για afm_called_by)
            username: Ειδικός κωδικός λήψης στοιχείων - Username
            password: Ειδικός κωδικός λήψης στοιχείων - Password
        """
        self.afm = afm
        self.username = username
        self.password = password
        self.session = requests.Session()

    def _build_soap_envelope(self, afm_called_by: str, afm_called_for: str) -> str:
        """
        Δημιουργεί το SOAP envelope για την αναζήτηση.

        Args:
            afm_called_by: ΑΦΜ του καλούντος (λογιστή)
            afm_called_for: ΑΦΜ προς αναζήτηση

        Returns:
            SOAP XML string
        """
        # Use proper GSIS namespace and element structure
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope"
              xmlns:ns1="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
              xmlns:ns2="http://gr/gsis/rgwspublic2/RgWsPublic2">
    <env:Header/>
    <env:Body>
        <ns2:rgWsPublic2AfmMethod>
            <ns2:INPUT_REC>
                <ns2:afm_called_by>{afm_called_by}</ns2:afm_called_by>
                <ns2:afm_called_for>{afm_called_for}</ns2:afm_called_for>
            </ns2:INPUT_REC>
        </ns2:rgWsPublic2AfmMethod>
    </env:Body>
</env:Envelope>'''

    def _parse_response(self, xml_response: str) -> AFMInfo:
        """
        Αναλύει την XML απάντηση του GSIS.

        Args:
            xml_response: XML string από το GSIS

        Returns:
            AFMInfo object με τα στοιχεία

        Raises:
            GSISError: Αν υπάρχει σφάλμα στην απάντηση
        """
        try:
            root = ET.fromstring(xml_response)
        except ET.ParseError as e:
            logger.error(f"Failed to parse GSIS XML response: {e}")
            raise GSISError(f"Σφάλμα ανάλυσης XML: {e}")

        # Βρες το body (try SOAP 1.2 first, then SOAP 1.1)
        body = root.find('.//env:Body', NAMESPACES)
        if body is None:
            body = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
        if body is None:
            body = root.find('.//soap:Body', NAMESPACES)
        if body is None:
            body = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')

        if body is None:
            raise GSISError("Δεν βρέθηκε το SOAP Body στην απάντηση")

        # Ελέγξου για SOAP Fault (both SOAP 1.1 and 1.2)
        fault = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Fault')
        if fault is None:
            fault = body.find('.//soap:Fault', NAMESPACES)
        if fault is None:
            fault = body.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')

        if fault is not None:
            fault_string = fault.findtext('faultstring', 'Άγνωστο σφάλμα')
            raise GSISError(f"SOAP Fault: {fault_string}")

        # Εξαγωγή δεδομένων - ψάξε για τα στοιχεία
        # Το GSIS επιστρέφει τα δεδομένα σε διάφορα tags
        data = {}

        # Helper function για να βρούμε text από element
        def get_text(parent, tag, default=''):
            # Try different namespace combinations
            el = parent.find(f'.//rgws:{tag}', NAMESPACES)
            if el is None:
                el = parent.find(f'.//{{{NAMESPACES["rgws"]}}}{tag}')
            if el is None:
                # Try without namespace
                el = parent.find(f'.//{tag}')
            if el is None:
                # Try to find anywhere
                for elem in parent.iter():
                    if elem.tag.endswith(tag):
                        return elem.text or default
            return el.text if el is not None and el.text else default

        # Έλεγχος για error code
        error_code = get_text(body, 'error_code')
        if error_code and error_code != '':
            error_msg = get_text(body, 'error_descr', 'Άγνωστο σφάλμα')
            raise GSISError(error_msg, error_code)

        # Εξαγωγή βασικών στοιχείων
        afm = get_text(body, 'afm')
        doy = get_text(body, 'doy')
        doy_descr = get_text(body, 'doy_descr')
        onomasia = get_text(body, 'onomasia')
        legal_form = get_text(body, 'legal_status_descr', '')
        legal_form_descr = get_text(body, 'legal_status_descr', '')

        # Flags
        deactivation = get_text(body, 'deactivation_flag', '1')
        deactivation_descr = get_text(body, 'deactivation_flag_descr', '')
        firm_flag = get_text(body, 'firm_flag_descr', '')

        # Διεύθυνση
        postal_address = get_text(body, 'postal_address')
        postal_address_no = get_text(body, 'postal_address_no')
        postal_zip_code = get_text(body, 'postal_zip_code')
        postal_area = get_text(body, 'postal_area_description')

        # Ημερομηνίες
        registration_date = get_text(body, 'regist_date')
        stop_date = get_text(body, 'stop_date')

        # Δραστηριότητες
        activities = []
        for activity in body.iter():
            if 'firm_act_descr' in activity.tag:
                act_data = {}
                parent = activity.getparent() if hasattr(activity, 'getparent') else None
                if parent is not None:
                    for child in parent:
                        tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        act_data[tag_name] = child.text
                    if act_data:
                        activities.append(act_data)

        # Αν δεν βρήκαμε activities με τον παραπάνω τρόπο, δοκίμασε αλλιώς
        if not activities:
            main_activity = get_text(body, 'firm_act_descr')
            if main_activity:
                activities.append({
                    'firm_act_descr': main_activity,
                    'firm_act_kind': get_text(body, 'firm_act_kind', '1'),
                    'firm_act_kind_descr': get_text(body, 'firm_act_kind_descr', 'ΚΥΡΙΑ'),
                })

        # Raw data για debugging
        raw_data = {
            'xml_response': xml_response[:1000] if len(xml_response) > 1000 else xml_response
        }

        return AFMInfo(
            afm=afm,
            doy=doy,
            doy_descr=doy_descr,
            onomasia=onomasia,
            legal_form=legal_form,
            legal_form_descr=legal_form_descr,
            deactivation_flag=deactivation != '1',  # 1 = ενεργό, 2 = απενεργοποιημένο
            deactivation_flag_descr=deactivation_descr,
            firm_flag=firm_flag.lower() in ['ναι', 'yes', 'true', '1'],
            firm_flag_descr=firm_flag,
            registration_date=registration_date if registration_date else None,
            stop_date=stop_date if stop_date else None,
            postal_address=postal_address,
            postal_address_no=postal_address_no,
            postal_zip_code=postal_zip_code,
            postal_area=postal_area,
            activities=activities,
            raw_data=raw_data,
        )

    def lookup_afm(self, afm: str, afm_called_by: str = None) -> AFMInfo:
        """
        Αναζήτηση στοιχείων με ΑΦΜ.

        Args:
            afm: Το ΑΦΜ προς αναζήτηση
            afm_called_by: ΑΦΜ του καλούντος (optional, χρησιμοποιεί το username αν δεν δοθεί)

        Returns:
            AFMInfo με τα στοιχεία του ΑΦΜ

        Raises:
            GSISError: Αν υπάρχει σφάλμα
        """
        # Validation
        if not afm or len(afm) != 9 or not afm.isdigit():
            raise GSISError("Μη έγκυρο ΑΦΜ. Πρέπει να είναι 9 ψηφία.")

        # Αν δεν δόθηκε afm_called_by, χρησιμοποίησε το ΑΦΜ του λογιστή
        if not afm_called_by:
            afm_called_by = self.afm

        # Build SOAP request
        soap_envelope = self._build_soap_envelope(afm_called_by, afm)

        # SOAP 1.2 uses application/soap+xml, SOAPAction in Content-Type
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://gr/gsis/rgwspublic2/RgWsPublic2/rgWsPublic2AfmMethod"',
        }

        logger.info(f"Looking up AFM: {afm}")

        try:
            response = self.session.post(
                GSIS_WSDL_URL,
                data=soap_envelope.encode('utf-8'),
                headers=headers,
                auth=(self.username, self.password),
                timeout=30,
            )

            logger.debug(f"GSIS Response status: {response.status_code}")

            if response.status_code == 401:
                raise GSISError("Σφάλμα αυθεντικοποίησης. Ελέγξτε τα credentials.")

            if response.status_code != 200:
                raise GSISError(f"HTTP Error: {response.status_code}")

            return self._parse_response(response.text)

        except requests.RequestException as e:
            logger.error(f"GSIS request failed: {e}")
            raise GSISError(f"Σφάλμα σύνδεσης με GSIS: {e}")

    def test_connection(self) -> bool:
        """
        Δοκιμάζει τη σύνδεση με το GSIS.

        Returns:
            True αν η σύνδεση είναι επιτυχής
        """
        try:
            # Δοκίμασε με ένα γνωστό ΑΦΜ (π.χ. ΔΕΗ)
            self.lookup_afm('090000045')
            return True
        except GSISError as e:
            # Αν το σφάλμα είναι authentication, η σύνδεση απέτυχε
            if 'αυθεντικοποίησης' in str(e).lower() or '401' in str(e):
                return False
            # Άλλα σφάλματα (π.χ. invalid AFM) σημαίνουν ότι η σύνδεση λειτουργεί
            return True
        except Exception:
            return False


def get_gsis_client():
    """
    Επιστρέφει GSISClient με τα credentials από τη βάση.

    Returns:
        GSISClient instance ή None αν δεν υπάρχουν credentials
    """
    from settings.models import GSISSettings

    settings = GSISSettings.get_settings()
    if not settings or not settings.is_active:
        return None

    return GSISClient(
        afm=settings.afm,
        username=settings.username,
        password=settings.password,
    )


def lookup_afm(afm: str) -> Optional[AFMInfo]:
    """
    Shortcut function για αναζήτηση ΑΦΜ.

    Args:
        afm: Το ΑΦΜ προς αναζήτηση

    Returns:
        AFMInfo ή None αν δεν υπάρχουν credentials

    Raises:
        GSISError: Αν υπάρχει σφάλμα
    """
    client = get_gsis_client()
    if not client:
        raise GSISError("Δεν έχουν ρυθμιστεί τα credentials GSIS.")

    return client.lookup_afm(afm)
