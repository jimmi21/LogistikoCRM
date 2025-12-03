# -*- coding: utf-8 -*-
"""
accounting/api_obligations.py
Author: Claude
Description: REST API ViewSet for MonthlyObligation management
"""

from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, CharFilter,
    NumberFilter, DateFilter
)
from django.utils import timezone
from django.db.models import Q

from .models import MonthlyObligation, ClientProfile, ObligationType, ClientDocument


class ObligationPagination(PageNumberPagination):
    """Pagination for obligation list"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ObligationFilter(FilterSet):
    """Filter for MonthlyObligation"""
    client = NumberFilter(field_name='client_id')
    status = CharFilter(field_name='status')
    month = NumberFilter(field_name='month')
    year = NumberFilter(field_name='year')
    type = CharFilter(field_name='obligation_type__code')
    deadline_from = DateFilter(field_name='deadline', lookup_expr='gte')
    deadline_to = DateFilter(field_name='deadline', lookup_expr='lte')
    search = CharFilter(method='filter_search')

    class Meta:
        model = MonthlyObligation
        fields = ['client', 'status', 'month', 'year', 'type']

    def filter_search(self, queryset, name, value):
        """Search by client name, AFM, or obligation type"""
        if value:
            return queryset.filter(
                Q(client__eponimia__icontains=value) |
                Q(client__afm__icontains=value) |
                Q(obligation_type__name__icontains=value) |
                Q(obligation_type__code__icontains=value)
            )
        return queryset


# ============================================
# OBLIGATION SERIALIZERS
# ============================================

class ObligationTypeSerializer(serializers.ModelSerializer):
    """Serializer for ObligationType"""

    class Meta:
        model = ObligationType
        fields = ['id', 'code', 'name', 'frequency', 'deadline_type', 'deadline_day']


class ObligationListSerializer(serializers.ModelSerializer):
    """Serializer for obligation list view"""
    client_name = serializers.CharField(source='client.eponimia', read_only=True)
    client_afm = serializers.CharField(source='client.afm', read_only=True)
    type_name = serializers.CharField(source='obligation_type.name', read_only=True)
    type_code = serializers.CharField(source='obligation_type.code', read_only=True)
    period = serializers.SerializerMethodField()
    days_until_deadline = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = MonthlyObligation
        fields = [
            'id', 'client', 'client_name', 'client_afm',
            'obligation_type', 'type_name', 'type_code',
            'year', 'month', 'period', 'deadline', 'status',
            'days_until_deadline', 'is_overdue'
        ]

    def get_period(self, obj):
        return f"{obj.month:02d}/{obj.year}"


class ObligationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single obligation view"""
    client_name = serializers.CharField(source='client.eponimia', read_only=True)
    client_afm = serializers.CharField(source='client.afm', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    type_name = serializers.CharField(source='obligation_type.name', read_only=True)
    type_code = serializers.CharField(source='obligation_type.code', read_only=True)
    period = serializers.SerializerMethodField()
    days_until_deadline = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    deadline_status = serializers.CharField(read_only=True)
    cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    completed_by_username = serializers.CharField(
        source='completed_by.username', read_only=True
    )
    documents = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyObligation
        fields = [
            'id', 'client', 'client_name', 'client_afm', 'client_email',
            'obligation_type', 'type_name', 'type_code',
            'year', 'month', 'period', 'deadline', 'status',
            'completed_date', 'completed_by', 'completed_by_username',
            'notes', 'time_spent', 'hourly_rate', 'cost',
            'days_until_deadline', 'is_overdue', 'deadline_status',
            'attachment', 'attachment_url', 'attachments', 'documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_by']

    def get_period(self, obj):
        return f"{obj.month:02d}/{obj.year}"

    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None

    def get_documents(self, obj):
        """Get related documents for this obligation"""
        docs = ClientDocument.objects.filter(
            client=obj.client,
            obligation=obj
        )
        from .serializers import ClientDocumentSerializer
        return ClientDocumentSerializer(
            docs, many=True, context=self.context
        ).data


class ObligationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating obligations"""

    class Meta:
        model = MonthlyObligation
        fields = [
            'client', 'obligation_type', 'year', 'month',
            'deadline', 'status', 'notes', 'time_spent', 'hourly_rate'
        ]

    def validate(self, data):
        """Validate unique together constraint"""
        client = data.get('client')
        obligation_type = data.get('obligation_type')
        year = data.get('year')
        month = data.get('month')

        # Check for existing obligation (only on create)
        if not self.instance:
            exists = MonthlyObligation.objects.filter(
                client=client,
                obligation_type=obligation_type,
                year=year,
                month=month
            ).exists()
            if exists:
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Υπάρχει ήδη υποχρέωση για αυτόν τον πελάτη, "
                        f"τύπο και περίοδο ({month:02d}/{year})."
                    ]
                })

        # Validate month range
        if month and (month < 1 or month > 12):
            raise serializers.ValidationError({
                'month': "Ο μήνας πρέπει να είναι από 1 έως 12."
            })

        return data


# ============================================
# OBLIGATION VIEWSET
# ============================================

class ObligationViewSet(viewsets.ModelViewSet):
    """
    REST API ViewSet for MonthlyObligation

    Endpoints:
    - GET /api/obligations/ - List all (with filters)
    - GET /api/obligations/{id}/ - Get single
    - POST /api/obligations/ - Create
    - PUT /api/obligations/{id}/ - Update
    - PATCH /api/obligations/{id}/complete/ - Mark as complete
    - DELETE /api/obligations/{id}/ - Delete
    """
    queryset = MonthlyObligation.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = ObligationPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ObligationFilter
    ordering_fields = ['deadline', 'client__eponimia', 'status', 'created_at']
    ordering = ['deadline']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ObligationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ObligationCreateUpdateSerializer
        return ObligationDetailSerializer

    def get_queryset(self):
        """Optimize queryset with select_related"""
        return super().get_queryset().select_related(
            'client', 'obligation_type', 'completed_by'
        )

    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """
        PATCH /api/obligations/{id}/complete/
        Mark an obligation as completed
        """
        obligation = self.get_object()

        if obligation.status == 'completed':
            return Response(
                {'error': 'Η υποχρέωση είναι ήδη ολοκληρωμένη.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update obligation
        obligation.status = 'completed'
        obligation.completed_date = timezone.now().date()
        obligation.completed_by = request.user

        # Optional: time spent and notes from request
        if 'time_spent' in request.data:
            obligation.time_spent = request.data['time_spent']
        if 'notes' in request.data:
            obligation.notes = request.data.get('notes', '')

        obligation.save()

        serializer = ObligationDetailSerializer(
            obligation, context={'request': request}
        )
        return Response({
            'message': 'Η υποχρέωση ολοκληρώθηκε επιτυχώς.',
            'obligation': serializer.data
        })

    @action(detail=False, methods=['get'])
    def types(self, request):
        """
        GET /api/obligations/types/
        Get all active obligation types
        """
        types = ObligationType.objects.filter(is_active=True).order_by('priority', 'name')
        serializer = ObligationTypeSerializer(types, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        GET /api/obligations/overdue/
        Get all overdue obligations
        """
        today = timezone.now().date()
        overdue = self.get_queryset().filter(
            status__in=['pending', 'overdue'],
            deadline__lt=today
        ).order_by('deadline')

        # Update status to overdue if needed
        overdue.update(status='overdue')

        page = self.paginate_queryset(overdue)
        if page is not None:
            serializer = ObligationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ObligationListSerializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        GET /api/obligations/upcoming/
        Get obligations with deadline in next 7 days
        """
        today = timezone.now().date()
        from datetime import timedelta
        next_week = today + timedelta(days=7)

        upcoming = self.get_queryset().filter(
            status='pending',
            deadline__gte=today,
            deadline__lte=next_week
        ).order_by('deadline')

        page = self.paginate_queryset(upcoming)
        if page is not None:
            serializer = ObligationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ObligationListSerializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_complete(self, request):
        """
        POST /api/obligations/bulk_complete/
        Mark multiple obligations as completed

        Body: {"obligation_ids": [1, 2, 3]}
        """
        obligation_ids = request.data.get('obligation_ids', [])

        if not obligation_ids:
            return Response(
                {'error': 'Δεν δόθηκαν IDs υποχρεώσεων.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obligations = MonthlyObligation.objects.filter(
            id__in=obligation_ids,
            status__in=['pending', 'overdue']
        )

        updated_count = obligations.update(
            status='completed',
            completed_date=timezone.now().date(),
            completed_by=request.user
        )

        return Response({
            'message': f'{updated_count} υποχρεώσεις ολοκληρώθηκαν.',
            'updated_count': updated_count
        })
