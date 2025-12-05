# -*- coding: utf-8 -*-
"""
accounting/api_obligation_profiles.py
Author: Claude
Description: REST API for Client Obligation Profiles and Monthly Generation

Endpoints:
- GET  /api/v1/clients/{id}/obligation-profile/  - Get client's obligation profile
- PUT  /api/v1/clients/{id}/obligation-profile/  - Update client's obligation profile
- GET  /api/v1/obligation-types/grouped/         - Get obligation types grouped by category
- GET  /api/v1/obligation-profiles/              - Get reusable obligation profiles
- POST /api/v1/obligations/generate-month/       - Generate monthly obligations from profiles
"""

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import (
    ClientProfile,
    ClientObligation,
    ObligationType,
    ObligationGroup,
    ObligationProfile,
    MonthlyObligation,
)


# ============================================
# SERIALIZERS
# ============================================

class ObligationTypeGroupedSerializer(serializers.ModelSerializer):
    """Serializer for ObligationType with group info"""
    group_name = serializers.CharField(source='exclusion_group.name', read_only=True, default='Χωρίς ομάδα')
    group_id = serializers.IntegerField(source='exclusion_group.id', read_only=True, default=None)

    class Meta:
        model = ObligationType
        fields = ['id', 'name', 'code', 'frequency', 'group_id', 'group_name', 'deadline_type', 'deadline_day']


class ObligationProfileSerializer(serializers.ModelSerializer):
    """Serializer for ObligationProfile (reusable bundles)"""
    obligation_types = ObligationTypeGroupedSerializer(source='obligations', many=True, read_only=True)

    class Meta:
        model = ObligationProfile
        fields = ['id', 'name', 'description', 'obligation_types']


class ClientObligationProfileSerializer(serializers.Serializer):
    """Serializer for client's obligation profile response"""
    client_id = serializers.IntegerField()
    obligation_type_ids = serializers.ListField(child=serializers.IntegerField())
    obligation_types = ObligationTypeGroupedSerializer(many=True)
    obligation_profile_ids = serializers.ListField(child=serializers.IntegerField())
    obligation_profiles = ObligationProfileSerializer(many=True)


# ============================================
# CLIENT OBLIGATION PROFILE ENDPOINTS
# ============================================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def client_obligation_profile(request, client_id):
    """
    GET /api/v1/clients/{id}/obligation-profile/
    Returns the client's obligation profile (which obligations they have)

    PUT /api/v1/clients/{id}/obligation-profile/
    Updates the client's obligation profile
    Body: { obligation_type_ids: [1,2,3], obligation_profile_ids: [1] }
    """
    client = get_object_or_404(ClientProfile, pk=client_id)

    # Get or create the ClientObligation record
    client_obligation, created = ClientObligation.objects.get_or_create(
        client=client,
        defaults={'is_active': True}
    )

    if request.method == 'GET':
        # Get individual obligation types
        obligation_types = list(client_obligation.obligation_types.filter(is_active=True))
        obligation_type_ids = [ot.id for ot in obligation_types]

        # Get profiles
        profiles = list(client_obligation.obligation_profiles.all())
        profile_ids = [p.id for p in profiles]

        # Serialize
        types_serializer = ObligationTypeGroupedSerializer(obligation_types, many=True)
        profiles_serializer = ObligationProfileSerializer(profiles, many=True)

        return Response({
            'client_id': client_id,
            'obligation_type_ids': obligation_type_ids,
            'obligation_types': types_serializer.data,
            'obligation_profile_ids': profile_ids,
            'obligation_profiles': profiles_serializer.data,
        })

    elif request.method == 'PUT':
        obligation_type_ids = request.data.get('obligation_type_ids', [])
        obligation_profile_ids = request.data.get('obligation_profile_ids', [])

        # Update obligation types
        if obligation_type_ids is not None:
            obligation_types = ObligationType.objects.filter(
                id__in=obligation_type_ids,
                is_active=True
            )
            client_obligation.obligation_types.set(obligation_types)

        # Update profiles
        if obligation_profile_ids is not None:
            profiles = ObligationProfile.objects.filter(id__in=obligation_profile_ids)
            client_obligation.obligation_profiles.set(profiles)

        client_obligation.is_active = True
        client_obligation.save()

        return Response({
            'success': True,
            'message': 'Το προφίλ υποχρεώσεων ενημερώθηκε επιτυχώς.'
        })


# ============================================
# OBLIGATION TYPES GROUPED ENDPOINT
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obligation_types_grouped(request):
    """
    GET /api/v1/obligation-types/grouped/
    Returns obligation types grouped by their exclusion_group (category)

    Response:
    [
        {
            group_id: 1,
            group_name: "Φορολογικά",
            types: [{ id, name, code, frequency }, ...]
        },
        ...
    ]
    """
    # Get all groups
    groups = ObligationGroup.objects.all().order_by('name')

    # Get all active types
    types = ObligationType.objects.filter(is_active=True).select_related('exclusion_group').order_by('priority', 'name')

    # Group types by their exclusion_group
    result = []

    # First, add groups with their types
    for group in groups:
        group_types = [t for t in types if t.exclusion_group_id == group.id]
        if group_types:
            result.append({
                'group_id': group.id,
                'group_name': group.name,
                'types': ObligationTypeGroupedSerializer(group_types, many=True).data
            })

    # Add types without a group
    ungrouped_types = [t for t in types if t.exclusion_group_id is None]
    if ungrouped_types:
        result.append({
            'group_id': None,
            'group_name': 'Λοιπά',
            'types': ObligationTypeGroupedSerializer(ungrouped_types, many=True).data
        })

    return Response(result)


# ============================================
# OBLIGATION PROFILES ENDPOINT
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obligation_profiles_list(request):
    """
    GET /api/v1/obligation-profiles/
    Returns all reusable obligation profiles
    """
    profiles = ObligationProfile.objects.all().prefetch_related('obligations')
    serializer = ObligationProfileSerializer(profiles, many=True)
    return Response(serializer.data)


# ============================================
# GENERATE MONTHLY OBLIGATIONS ENDPOINT
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_month_obligations(request):
    """
    POST /api/v1/obligations/generate-month/
    Generate monthly obligations for clients based on their obligation profiles

    Body: {
        month: 1,           # Required: 1-12
        year: 2025,         # Required
        client_ids: [1,2,3] # Optional: if empty, generate for ALL active clients
    }

    Response: {
        created_count: 25,
        skipped_count: 5,
        clients_processed: 10,
        details: [
            { client_id: 1, client_name: "...", created: ["ΦΠΑ", "ΑΠΔ"], skipped: ["ΕΝΦΙΑ"] }
        ]
    }
    """
    month = request.data.get('month')
    year = request.data.get('year')
    client_ids = request.data.get('client_ids', [])

    # Validation
    if not month or not year:
        return Response(
            {'error': 'Απαιτούνται μήνας και έτος.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Μη έγκυρος μήνας ή έτος.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if month < 1 or month > 12:
        return Response(
            {'error': 'Ο μήνας πρέπει να είναι 1-12.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get clients
    if client_ids:
        clients = ClientProfile.objects.filter(id__in=client_ids, is_active=True)
    else:
        clients = ClientProfile.objects.filter(is_active=True)

    if not clients.exists():
        return Response(
            {'error': 'Δεν βρέθηκαν ενεργοί πελάτες.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    created_count = 0
    skipped_count = 0
    details = []

    with transaction.atomic():
        for client in clients:
            client_created = []
            client_skipped = []

            # Get client's obligation settings
            try:
                client_obligation = ClientObligation.objects.get(client=client, is_active=True)
            except ClientObligation.DoesNotExist:
                # Client has no obligation profile configured
                details.append({
                    'client_id': client.id,
                    'client_name': client.eponimia,
                    'created': [],
                    'skipped': [],
                    'note': 'Δεν έχει ρυθμιστεί προφίλ υποχρεώσεων'
                })
                continue

            # Get all obligation types for this client
            all_types = client_obligation.get_all_obligation_types()

            for obligation_type in all_types:
                # Check if this type applies to this month
                if not obligation_type.applies_to_month(month):
                    continue

                # Check if obligation already exists
                existing = MonthlyObligation.objects.filter(
                    client=client,
                    obligation_type=obligation_type,
                    year=year,
                    month=month
                ).exists()

                if existing:
                    client_skipped.append(obligation_type.name)
                    skipped_count += 1
                    continue

                # Calculate deadline
                deadline = obligation_type.get_deadline_for_month(year, month)
                if not deadline:
                    from calendar import monthrange
                    last_day = monthrange(year, month)[1]
                    deadline = timezone.datetime(year, month, last_day).date()

                # Create the obligation
                MonthlyObligation.objects.create(
                    client=client,
                    obligation_type=obligation_type,
                    year=year,
                    month=month,
                    deadline=deadline,
                    status='pending'
                )

                client_created.append(obligation_type.name)
                created_count += 1

            if client_created or client_skipped:
                details.append({
                    'client_id': client.id,
                    'client_name': client.eponimia,
                    'created': client_created,
                    'skipped': client_skipped
                })

    return Response({
        'success': True,
        'created_count': created_count,
        'skipped_count': skipped_count,
        'clients_processed': clients.count(),
        'details': details,
        'message': f'Δημιουργήθηκαν {created_count} υποχρεώσεις. Παραλείφθηκαν {skipped_count} (υπήρχαν ήδη).'
    }, status=status.HTTP_201_CREATED)
