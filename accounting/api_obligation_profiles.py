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
from datetime import date
from calendar import monthrange

from .models import ClientProfile, MonthlyObligation, ObligationType, ObligationProfile


# ============================================
# SERIALIZERS
# ============================================

class ObligationTypeGroupedSerializer(serializers.ModelSerializer):
    """Serializer for obligation types with group info"""
    group_id = serializers.IntegerField(source='profile.id', allow_null=True, default=None)
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = ObligationType
        fields = ['id', 'name', 'code', 'frequency', 'deadline_type', 'deadline_day', 'group_id', 'group_name']

    def get_group_name(self, obj):
        if obj.profile:
            return obj.profile.name
        return 'Χωρίς κατηγορία'


class ObligationGroupSerializer(serializers.Serializer):
    """Serializer for grouped obligation types"""
    id = serializers.IntegerField(allow_null=True)
    name = serializers.CharField()
    types = ObligationTypeGroupedSerializer(many=True)


class ClientObligationProfileSerializer(serializers.Serializer):
    """Serializer for client's obligation profile"""
    client_id = serializers.IntegerField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    obligation_types = serializers.ListField(child=serializers.IntegerField())
    bundle_id = serializers.IntegerField(allow_null=True, read_only=True)
    bundle_name = serializers.CharField(allow_null=True, read_only=True)


class GenerateMonthRequestSerializer(serializers.Serializer):
    """Serializer for generate month request"""
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2020, max_value=2100)
    client_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)


class GenerateMonthResultSerializer(serializers.Serializer):
    """Serializer for generate month result"""
    success = serializers.BooleanField()
    clients_processed = serializers.IntegerField()
    obligations_created = serializers.IntegerField()
    skipped_clients = serializers.ListField(child=serializers.CharField())
    errors = serializers.ListField(child=serializers.CharField())


# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_deadline(obligation_type, month, year):
    """Calculate the deadline for an obligation based on its type settings"""
    deadline_type = obligation_type.deadline_type
    deadline_day = obligation_type.deadline_day

    if deadline_type == 'last_day':
        # Last day of the current month
        last_day = monthrange(year, month)[1]
        return date(year, month, last_day)
    elif deadline_type == 'specific_day':
        # Specific day of the next month (e.g., 20th)
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        day = min(deadline_day or 20, monthrange(next_year, next_month)[1])
        return date(next_year, next_month, day)
    elif deadline_type == 'last_day_prev':
        # Last day of the previous month
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        last_day = monthrange(prev_year, prev_month)[1]
        return date(prev_year, prev_month, last_day)
    elif deadline_type == 'last_day_next':
        # Last day of the next month
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        last_day = monthrange(next_year, next_month)[1]
        return date(next_year, next_month, last_day)
    else:
        # Default: 20th of next month
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        return date(next_year, next_month, 20)


def should_generate_obligation(obligation_type, month, year, client_vat_period=None):
    """Determine if an obligation should be generated for this month based on frequency"""
    frequency = obligation_type.frequency

    if frequency == 'monthly':
        return True
    elif frequency == 'quarterly':
        # Generate for months 3, 6, 9, 12
        return month in [3, 6, 9, 12]
    elif frequency == 'annual':
        # Generate only for specific months (usually determined by obligation type)
        # For now, generate in month 7 (July) for annual obligations
        return month == 7
    elif frequency == 'follows_vat':
        # Follow the client's VAT period (monthly or quarterly)
        if client_vat_period == 'quarterly':
            return month in [3, 6, 9, 12]
        return True  # Default to monthly
    else:
        return True


# ============================================
# API VIEWS
# ============================================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def client_obligation_profile(request, client_id):
    """
    GET: Retrieve client's obligation profile (selected obligation types)
    PUT: Update client's obligation profile
    """
    client = get_object_or_404(ClientProfile, pk=client_id)

    if request.method == 'GET':
        # Get client's selected obligation types
        obligation_types = list(client.obligation_types.values_list('id', flat=True))

        data = {
            'client_id': client.id,
            'client_name': str(client),
            'obligation_types': obligation_types,
            'bundle_id': None,  # Future: support for bundles
            'bundle_name': None,
        }
        return Response(data)

    elif request.method == 'PUT':
        serializer = ClientObligationProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update client's obligation types
        type_ids = serializer.validated_data.get('obligation_types', [])
        obligation_types = ObligationType.objects.filter(id__in=type_ids)
        client.obligation_types.set(obligation_types)

        # Return updated profile
        data = {
            'client_id': client.id,
            'client_name': str(client),
            'obligation_types': list(client.obligation_types.values_list('id', flat=True)),
            'bundle_id': None,
            'bundle_name': None,
        }
        return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obligation_types_grouped(request):
    """
    Get all obligation types grouped by their category/profile
    """
    # Get all profiles
    profiles = ObligationProfile.objects.prefetch_related('obligations').all()

    result = []

    # Add grouped types (using profile.obligations related_name)
    for profile in profiles:
        types = profile.obligations.filter(is_active=True)
        if types.exists():
            result.append({
                'id': profile.id,
                'name': profile.name,
                'types': ObligationTypeGroupedSerializer(types, many=True).data
            })

    # Add ungrouped types
    ungrouped = ObligationType.objects.filter(profile__isnull=True, is_active=True)
    if ungrouped.exists():
        result.append({
            'id': None,
            'name': 'Χωρίς κατηγορία',
            'types': ObligationTypeGroupedSerializer(ungrouped, many=True).data
        })

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obligation_profiles_list(request):
    """
    Get list of reusable obligation profile bundles (for future use)
    Currently returns an empty list as bundles are not yet implemented
    """
    # Future implementation: ObligationProfileBundle model
    return Response([])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_month_obligations(request):
    """
    Generate monthly obligations for clients based on their obligation profiles

    Request body:
    {
        "month": 1-12,
        "year": 2020-2100,
        "client_ids": [1, 2, 3]  // Optional: specific clients, or all if omitted
    }

    Response:
    {
        "success": true,
        "clients_processed": 10,
        "obligations_created": 25,
        "skipped_clients": ["Client A", "Client B"],
        "errors": []
    }
    """
    serializer = GenerateMonthRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    month = serializer.validated_data['month']
    year = serializer.validated_data['year']
    client_ids = serializer.validated_data.get('client_ids')

    # Get clients to process
    if client_ids:
        clients = ClientProfile.objects.filter(id__in=client_ids, is_active=True)
    else:
        clients = ClientProfile.objects.filter(is_active=True)

    # Filter to only clients with obligation profiles set
    clients = clients.prefetch_related('obligation_types').filter(obligation_types__isnull=False).distinct()

    clients_processed = 0
    obligations_created = 0
    skipped_clients = []
    errors = []

    with transaction.atomic():
        for client in clients:
            client_obligation_types = client.obligation_types.all()

            if not client_obligation_types.exists():
                skipped_clients.append(str(client))
                continue

            clients_processed += 1

            for obl_type in client_obligation_types:
                try:
                    # Check if this obligation should be generated for this month
                    if not should_generate_obligation(obl_type, month, year):
                        continue

                    # Check if obligation already exists
                    existing = MonthlyObligation.objects.filter(
                        client=client,
                        obligation_type=obl_type,
                        month=month,
                        year=year
                    ).exists()

                    if existing:
                        continue

                    # Calculate deadline
                    deadline = calculate_deadline(obl_type, month, year)

                    # Create the obligation
                    MonthlyObligation.objects.create(
                        client=client,
                        obligation_type=obl_type,
                        month=month,
                        year=year,
                        deadline=deadline,
                        status='pending',
                    )
                    obligations_created += 1

                except Exception as e:
                    errors.append(f"Error for {client}: {str(e)}")

    result = {
        'success': len(errors) == 0,
        'clients_processed': clients_processed,
        'obligations_created': obligations_created,
        'skipped_clients': skipped_clients,
        'errors': errors,
    }

    return Response(result)
