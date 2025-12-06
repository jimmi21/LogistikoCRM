# -*- coding: utf-8 -*-
"""
Export/Import API for LogistikoCRM
===================================
Handles CSV/Excel export and import for clients and obligation profiles.
"""
import csv
import io
from datetime import datetime

from django.http import HttpResponse
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ClientProfile, ObligationType, ObligationProfile, ClientObligation


# ==============================================================================
# CLIENT EXPORT
# ==============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_clients_csv(request):
    """
    GET /api/v1/export/clients/csv/
    Export all clients to CSV file.
    """
    # Create the HttpResponse object with CSV content type
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="clients_{timestamp}.csv"'

    # Add BOM for Excel UTF-8 compatibility
    response.write('\ufeff')

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        'ID',
        'ΑΦΜ',
        'Επωνυμία',
        'Email',
        'Τηλέφωνο',
        'Κινητό',
        'ΔΟΥ',
        'Διεύθυνση',
        'Πόλη',
        'ΤΚ',
        'Υπεύθυνος',
        'Σημειώσεις',
        'Ενεργός',
        'Ημ. Δημιουργίας',
    ])

    # Data rows
    clients = ClientProfile.objects.all().order_by('onoma')
    for client in clients:
        writer.writerow([
            client.id,
            client.afm or '',
            client.onoma or '',
            client.email or '',
            client.phone or '',
            client.mobile or '',
            client.doy or '',
            client.address or '',
            client.city or '',
            client.postal_code or '',
            client.contact_person or '',
            client.notes or '',
            'Ναι' if client.is_active else 'Όχι',
            client.created.strftime('%Y-%m-%d') if client.created else '',
        ])

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_clients_template(request):
    """
    GET /api/v1/export/clients/template/
    Export empty CSV template for client import.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="clients_template.csv"'

    # Add BOM for Excel UTF-8 compatibility
    response.write('\ufeff')

    writer = csv.writer(response)

    # Header row with instructions
    writer.writerow([
        'ΑΦΜ (υποχρεωτικό)',
        'Επωνυμία (υποχρεωτικό)',
        'Email',
        'Τηλέφωνο',
        'Κινητό',
        'ΔΟΥ',
        'Διεύθυνση',
        'Πόλη',
        'ΤΚ',
        'Υπεύθυνος',
        'Σημειώσεις',
    ])

    # Example row
    writer.writerow([
        '123456789',
        'ΠΑΡΑΔΕΙΓΜΑ ΑΕ',
        'info@example.com',
        '2101234567',
        '6971234567',
        'ΑΘΗΝΩΝ',
        'Οδός Παραδείγματος 1',
        'Αθήνα',
        '10000',
        'Ιωάννης Παπαδόπουλος',
        'Σημειώσεις εδώ',
    ])

    return response


# ==============================================================================
# CLIENT IMPORT
# ==============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def import_clients_csv(request):
    """
    POST /api/v1/import/clients/csv/
    Import clients from CSV file.

    Form data:
        - file: CSV file
        - mode: 'skip' (skip duplicates) or 'update' (update existing)
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'Δεν επιλέχθηκε αρχείο.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    csv_file = request.FILES['file']
    mode = request.data.get('mode', 'skip')  # 'skip' or 'update'

    # Check file extension
    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'Μόνο αρχεία CSV επιτρέπονται.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Read and decode the file
        decoded_file = csv_file.read().decode('utf-8-sig')  # Handle BOM
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        # Map possible column names to field names
        field_mapping = {
            'ΑΦΜ (υποχρεωτικό)': 'afm',
            'ΑΦΜ': 'afm',
            'afm': 'afm',
            'Επωνυμία (υποχρεωτικό)': 'onoma',
            'Επωνυμία': 'onoma',
            'onoma': 'onoma',
            'Email': 'email',
            'email': 'email',
            'Τηλέφωνο': 'phone',
            'phone': 'phone',
            'Κινητό': 'mobile',
            'mobile': 'mobile',
            'ΔΟΥ': 'doy',
            'doy': 'doy',
            'Διεύθυνση': 'address',
            'address': 'address',
            'Πόλη': 'city',
            'city': 'city',
            'ΤΚ': 'postal_code',
            'postal_code': 'postal_code',
            'Υπεύθυνος': 'contact_person',
            'contact_person': 'contact_person',
            'Σημειώσεις': 'notes',
            'notes': 'notes',
        }

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                # Map row to field names
                data = {}
                for col_name, value in row.items():
                    if col_name in field_mapping:
                        data[field_mapping[col_name]] = value.strip() if value else ''

                # Validate required fields
                afm = data.get('afm', '').strip()
                onoma = data.get('onoma', '').strip()

                if not afm:
                    errors.append(f'Γραμμή {row_num}: Λείπει το ΑΦΜ')
                    continue

                if not onoma:
                    errors.append(f'Γραμμή {row_num}: Λείπει η επωνυμία')
                    continue

                # Validate AFM format (9 digits)
                if len(afm) != 9 or not afm.isdigit():
                    errors.append(f'Γραμμή {row_num}: Μη έγκυρο ΑΦΜ "{afm}"')
                    continue

                # Check if client exists
                existing = ClientProfile.objects.filter(afm=afm).first()

                if existing:
                    if mode == 'update':
                        # Update existing client
                        existing.onoma = onoma
                        existing.email = data.get('email', '') or existing.email
                        existing.phone = data.get('phone', '') or existing.phone
                        existing.mobile = data.get('mobile', '') or existing.mobile
                        existing.doy = data.get('doy', '') or existing.doy
                        existing.address = data.get('address', '') or existing.address
                        existing.city = data.get('city', '') or existing.city
                        existing.postal_code = data.get('postal_code', '') or existing.postal_code
                        existing.contact_person = data.get('contact_person', '') or existing.contact_person
                        existing.notes = data.get('notes', '') or existing.notes
                        existing.save()
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Create new client
                    ClientProfile.objects.create(
                        afm=afm,
                        onoma=onoma,
                        email=data.get('email', ''),
                        phone=data.get('phone', ''),
                        mobile=data.get('mobile', ''),
                        doy=data.get('doy', ''),
                        address=data.get('address', ''),
                        city=data.get('city', ''),
                        postal_code=data.get('postal_code', ''),
                        contact_person=data.get('contact_person', ''),
                        notes=data.get('notes', ''),
                        is_active=True,
                    )
                    created_count += 1

        return Response({
            'success': True,
            'created_count': created_count,
            'updated_count': updated_count,
            'skipped_count': skipped_count,
            'errors': errors[:20],  # Limit errors shown
            'message': f'Δημιουργήθηκαν {created_count} πελάτες. Ενημερώθηκαν {updated_count}. Παραλείφθηκαν {skipped_count}.'
        })

    except Exception as e:
        return Response(
            {'error': f'Σφάλμα κατά την ανάγνωση του αρχείου: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ==============================================================================
# OBLIGATION PROFILES EXPORT
# ==============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_obligation_profiles_csv(request):
    """
    GET /api/v1/export/obligation-profiles/csv/
    Export all obligation profiles to CSV file.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="obligation_profiles_{timestamp}.csv"'

    # Add BOM for Excel UTF-8 compatibility
    response.write('\ufeff')

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        'ID',
        'Όνομα',
        'Περιγραφή',
        'Τύποι Υποχρεώσεων (κωδικοί)',
    ])

    # Data rows
    profiles = ObligationProfile.objects.all().prefetch_related('obligation_types')
    for profile in profiles:
        type_codes = ', '.join([ot.code for ot in profile.obligation_types.all()])
        writer.writerow([
            profile.id,
            profile.name or '',
            profile.description or '',
            type_codes,
        ])

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_obligation_types_csv(request):
    """
    GET /api/v1/export/obligation-types/csv/
    Export all obligation types to CSV file.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="obligation_types_{timestamp}.csv"'

    # Add BOM for Excel UTF-8 compatibility
    response.write('\ufeff')

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        'ID',
        'Κωδικός',
        'Όνομα',
        'Περιγραφή',
        'Συχνότητα',
        'Τύπος Προθεσμίας',
        'Ημέρα Προθεσμίας',
        'Ενεργός',
    ])

    # Data rows
    types = ObligationType.objects.all().order_by('code')
    for ot in types:
        writer.writerow([
            ot.id,
            ot.code or '',
            ot.name or '',
            ot.description or '',
            ot.frequency or '',
            ot.deadline_type or '',
            ot.deadline_day or '',
            'Ναι' if ot.is_active else 'Όχι',
        ])

    return response


# ==============================================================================
# CLIENT OBLIGATION PROFILES EXPORT
# ==============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_client_obligations_csv(request):
    """
    GET /api/v1/export/client-obligations/csv/
    Export client-obligation profile assignments to CSV.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="client_obligations_{timestamp}.csv"'

    # Add BOM for Excel UTF-8 compatibility
    response.write('\ufeff')

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        'ΑΦΜ Πελάτη',
        'Επωνυμία Πελάτη',
        'Προφίλ Υποχρεώσεων',
        'Μεμονωμένοι Τύποι Υποχρεώσεων',
    ])

    # Data rows
    client_obligations = ClientObligation.objects.all().select_related('client').prefetch_related(
        'obligation_profiles', 'obligation_types'
    )

    for co in client_obligations:
        profile_names = ', '.join([p.name for p in co.obligation_profiles.all()])
        type_codes = ', '.join([t.code for t in co.obligation_types.all()])
        writer.writerow([
            co.client.afm or '',
            co.client.onoma or '',
            profile_names,
            type_codes,
        ])

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def import_client_obligations_csv(request):
    """
    POST /api/v1/import/client-obligations/csv/
    Import client-obligation profile assignments from CSV.

    CSV Format:
        ΑΦΜ Πελάτη, Προφίλ Υποχρεώσεων (comma separated names)
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'Δεν επιλέχθηκε αρχείο.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    csv_file = request.FILES['file']
    mode = request.data.get('mode', 'add')  # 'add' or 'replace'

    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'Μόνο αρχεία CSV επιτρέπονται.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        decoded_file = csv_file.read().decode('utf-8-sig')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        # Preload profiles and types for quick lookup
        profiles_by_name = {p.name.lower(): p for p in ObligationProfile.objects.all()}
        types_by_code = {t.code.lower(): t for t in ObligationType.objects.filter(is_active=True)}

        updated_count = 0
        created_count = 0
        errors = []

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                afm = row.get('ΑΦΜ Πελάτη', '').strip()

                if not afm:
                    errors.append(f'Γραμμή {row_num}: Λείπει το ΑΦΜ')
                    continue

                client = ClientProfile.objects.filter(afm=afm).first()
                if not client:
                    errors.append(f'Γραμμή {row_num}: Δεν βρέθηκε πελάτης με ΑΦΜ {afm}')
                    continue

                # Parse profiles
                profile_names = [p.strip().lower() for p in row.get('Προφίλ Υποχρεώσεων', '').split(',') if p.strip()]
                type_codes = [t.strip().lower() for t in row.get('Μεμονωμένοι Τύποι Υποχρεώσεων', '').split(',') if t.strip()]

                # Get or create ClientObligation
                client_obligation, created = ClientObligation.objects.get_or_create(
                    client=client,
                    defaults={'is_active': True}
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                # Handle profiles
                profiles_to_assign = [profiles_by_name[name] for name in profile_names if name in profiles_by_name]
                types_to_assign = [types_by_code[code] for code in type_codes if code in types_by_code]

                if mode == 'replace':
                    client_obligation.obligation_profiles.set(profiles_to_assign)
                    client_obligation.obligation_types.set(types_to_assign)
                else:
                    for p in profiles_to_assign:
                        client_obligation.obligation_profiles.add(p)
                    for t in types_to_assign:
                        client_obligation.obligation_types.add(t)

        return Response({
            'success': True,
            'created_count': created_count,
            'updated_count': updated_count,
            'errors': errors[:20],
            'message': f'Ενημερώθηκαν {updated_count} πελάτες. Δημιουργήθηκαν {created_count} νέες αναθέσεις.'
        })

    except Exception as e:
        return Response(
            {'error': f'Σφάλμα: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
