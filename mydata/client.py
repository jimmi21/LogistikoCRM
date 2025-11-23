# mydata/client.py
"""
myDATA API Client για AADE
Documentation: https://www.aade.gr/mydata
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MyDataClient:
    """
    Client για το myDATA REST API της AADE
    """
    
    # Production URLs
    PROD_BASE_URL = "https://mydatapi.aade.gr/myDATA"
    
    # Sandbox URLs (για testing)
    SANDBOX_BASE_URL = "https://mydataapidev.aade.gr"
    
    def __init__(self, user_id: str, subscription_key: str, is_sandbox: bool = False):
        """
        Αρχικοποίηση client
        
        Args:
            user_id: Το user_id από το TAXISnet (username για test, AFM για production)
            subscription_key: Το subscription key από την AADE
            is_sandbox: True για testing, False για production
        """
        self.user_id = user_id
        self.subscription_key = subscription_key
        self.base_url = self.SANDBOX_BASE_URL if is_sandbox else self.PROD_BASE_URL
        self.session = requests.Session()
        
        # Default headers για όλα τα requests
        self.session.headers.update({
            'aade-user-id': self.user_id,
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """
        Helper για API requests
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint (π.χ. '/RequestDocs')
            **kwargs: Επιπλέον arguments για requests
            
        Returns:
            Dict με response data ή XML string
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            logger.info(f"myDATA API: {method} {endpoint} - Status {response.status_code}")
            
            if response.content:
                content_type = response.headers.get('Content-Type', '')
                if 'json' in content_type.lower():
                    return response.json()
                else:
                    # Return raw text (probably XML)
                    return response.text
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"myDATA API Error: {method} {endpoint} - {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    # =====================================================
    # ΛΗΜΨΗ ΠΑΡΑΣΤΑΤΙΚΩΝ (Incoming Invoices)
    # =====================================================
    
    def request_transmitted_docs(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        mark: Optional[int] = None
    ) -> Dict:
        """
        Λήψη παραστατικών που έχεις ΣΤΕΙΛΕΙ (εκδώσει)
        
        Args:
            date_from: Από ημερομηνία (default: χθες)
            date_to: Έως ημερομηνία (default: σήμερα)
            mark: MARK συγκεκριμένου παραστατικού
            
        Returns:
            Dict με λίστα παραστατικών
        """
        if not date_from:
            date_from = datetime.now() - timedelta(days=1)
        if not date_to:
            date_to = datetime.now()
        
        # Αν έχουμε mark, ζητάμε μόνο αυτό
        if mark:
            params = {'mark': mark}
        else:
            # Για test environment - NO PARAMETERS (get all)
            params = {}
        
        return self._make_request('GET', '/RequestTransmittedDocs', params=params)
    
    def request_docs(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        mark: Optional[int] = None
    ):
        """
        Λήψη παραστατικών που έχεις ΛΑΒΕΙ (από προμηθευτές)
        
        Args:
            date_from: Από ημερομηνία
            date_to: Έως ημερομηνία  
            mark: MARK συγκεκριμένου παραστατικού
            
        Returns:
            Dict/XML με λίστα παραστατικών
        """
        if not date_from:
            date_from = datetime.now() - timedelta(days=7)
        if not date_to:
            date_to = datetime.now()
        
        # Αν έχουμε mark, ζητάμε μόνο αυτό
        if mark:
            params = {'mark': mark}
        else:
            # Παίρνουμε όλα τα invoices από mark=0
            params = {
                'mark': 0,
                'dateFrom': date_from.strftime('%d/%m/%Y'),
                'dateTo': date_to.strftime('%d/%m/%Y')
            }
        
        return self._make_request('GET', '/RequestDocs', params=params)
    
    # =====================================================
    # ΑΠΟΣΤΟΛΗ ΠΑΡΑΣΤΑΤΙΚΩΝ (Send Invoices)
    # =====================================================
    
    def send_invoices(self, invoices_data: List[Dict]) -> Dict:
        """
        Αποστολή παραστατικών στο myDATA
        
        Args:
            invoices_data: List με invoice objects
            
        Returns:
            Dict με response (περιέχει MARK για κάθε παραστατικό)
        """
        payload = {"invoices": invoices_data}
        return self._make_request('POST', '/SendInvoices', json=payload)
    
    # =====================================================
    # ΑΚΥΡΩΣΗ ΠΑΡΑΣΤΑΤΙΚΩΝ
    # =====================================================
    
    def cancel_invoice(self, mark: int) -> Dict:
        """
        Ακύρωση παραστατικού
        
        Args:
            mark: Το MARK του παραστατικού προς ακύρωση
            
        Returns:
            Dict με response
        """
        payload = {
            "cancellationMark": mark,
            "cancellationDate": datetime.now().strftime('%d/%m/%Y')
        }
        return self._make_request('POST', '/CancelInvoice', json=payload)
    
    # =====================================================
    # HELPER METHODS
    # =====================================================
    
    def parse_invoice_response(self, response) -> List[Dict]:
        """
        Parse response από RequestDocs/RequestTransmittedDocs
        Supports both JSON and XML responses
        
        Returns:
            List με normalized invoices
        """
        invoices = []
        
        # If response is string (XML), parse it
        if isinstance(response, str):
            # Define namespaces
            ns = {'ns': 'http://www.aade.gr/myDATA/invoice/v1.0'}
            
            try:
                root = ET.fromstring(response)
                
                # Find all invoice elements
                for inv_elem in root.findall('.//ns:invoice', ns):
                    # Extract issuer
                    issuer = inv_elem.find('.//ns:issuer', ns)
                    issuer_vat = issuer.find('ns:vatNumber', ns).text if issuer is not None else None
                    
                    # Extract counterpart
                    counterpart = inv_elem.find('.//ns:counterpart', ns)
                    counterpart_vat = counterpart.find('ns:vatNumber', ns).text if counterpart is not None else None
                    
                    # Extract header
                    header = inv_elem.find('.//ns:invoiceHeader', ns)
                    if header is not None:
                        series_elem = header.find('ns:series', ns)
                        aa_elem = header.find('ns:aa', ns)
                        issue_date_elem = header.find('ns:issueDate', ns)
                        invoice_type_elem = header.find('ns:invoiceType', ns)
                        
                        series = series_elem.text if series_elem is not None else ''
                        aa = aa_elem.text if aa_elem is not None else ''
                        issue_date = issue_date_elem.text if issue_date_elem is not None else ''
                        invoice_type = invoice_type_elem.text if invoice_type_elem is not None else ''
                    else:
                        continue
                    
                    # Extract summary
                    summary = inv_elem.find('.//ns:invoiceSummary', ns)
                    if summary is not None:
                        total_net_elem = summary.find('ns:totalNetValue', ns)
                        total_vat_elem = summary.find('ns:totalVatAmount', ns)
                        total_gross_elem = summary.find('ns:totalGrossValue', ns)
                        
                        total_net = float(total_net_elem.text) if total_net_elem is not None and total_net_elem.text else 0
                        total_vat = float(total_vat_elem.text) if total_vat_elem is not None and total_vat_elem.text else 0
                        total_gross = float(total_gross_elem.text) if total_gross_elem is not None and total_gross_elem.text else 0
                    else:
                        total_net = total_vat = total_gross = 0
                    
                    invoices.append({
                        'mark': None,  # Mark not in XML, only in response wrapper
                        'uid': None,
                        'issuer_vat': issuer_vat,
                        'counterpart_vat': counterpart_vat,
                        'series': series,
                        'aa': aa,
                        'issue_date': issue_date,
                        'invoice_type': invoice_type,
                        'total_net': total_net,
                        'total_vat': total_vat,
                        'total_gross': total_gross,
                        'details': []
                    })
            except ET.ParseError as e:
                logger.error(f"XML Parse Error: {e}")
                return []
        
        # If response is dict (JSON)
        elif isinstance(response, dict) and 'invoices' in response:
            for inv in response['invoices']:
                invoices.append({
                    'mark': inv.get('mark'),
                    'uid': inv.get('uid'),
                    'issuer_vat': inv.get('issuer', {}).get('vatNumber'),
                    'counterpart_vat': inv.get('counterpart', {}).get('vatNumber'),
                    'series': inv.get('invoiceHeader', {}).get('series'),
                    'aa': inv.get('invoiceHeader', {}).get('aa'),
                    'issue_date': inv.get('invoiceHeader', {}).get('issueDate'),
                    'invoice_type': inv.get('invoiceHeader', {}).get('invoiceType'),
                    'total_net': inv.get('invoiceSummary', {}).get('totalNetValue'),
                    'total_vat': inv.get('invoiceSummary', {}).get('totalVatAmount'),
                    'total_gross': inv.get('invoiceSummary', {}).get('totalGrossValue'),
                    'details': inv.get('invoiceDetails', [])
                })
        
        return invoices
