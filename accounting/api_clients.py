# -*- coding: utf-8 -*-
"""
accounting/api_clients.py
Author: Claude
Description: REST API ViewSet for ClientProfile management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, BooleanFilter
from django.db.models import Count, Q

from .models import ClientProfile, MonthlyObligation, ClientDocument
from .serializers import ClientDocumentSerializer


class ClientPagination(PageNumberPagination):
    """Pagination for client list"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ClientFilter(FilterSet):
    """Filter for ClientProfile"""
    search = CharFilter(method='filter_search')
    is_active = BooleanFilter(field_name='is_active')

    class Meta:
        model = ClientProfile
        fields = ['is_active']

    def filter_search(self, queryset, name, value):
        """Search by name, afm, email, phone"""
        if value:
            return queryset.filter(
                Q(eponimia__icontains=value) |
                Q(afm__icontains=value) |
                Q(email__icontains=value) |
                Q(kinito_tilefono__icontains=value) |
                Q(tilefono_oikias_1__icontains=value) |
                Q(tilefono_epixeirisis_1__icontains=value)
            )
        return queryset


# ============================================
# CLIENT SERIALIZERS
# ============================================

from rest_framework import serializers


class ClientListSerializer(serializers.ModelSerializer):
    """Serializer for client list view"""

    class Meta:
        model = ClientProfile
        fields = [
            'id', 'afm', 'eponimia', 'email',
            'kinito_tilefono', 'is_active'
        ]


class ClientDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single client view"""
    obligations_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    pending_obligations_count = serializers.SerializerMethodField()

    class Meta:
        model = ClientProfile
        fields = [
            # Basic info
            'id', 'afm', 'doy', 'eponimia', 'onoma', 'onoma_patros',
            # Identity
            'arithmos_taftotitas', 'eidos_taftotitas', 'prosopikos_arithmos',
            'amka', 'am_ika', 'arithmos_gemi', 'arithmos_dypa',
            # Personal dates
            'imerominia_gennisis', 'imerominia_gamou', 'filo',
            # Home address
            'diefthinsi_katoikias', 'arithmos_katoikias', 'poli_katoikias',
            'dimos_katoikias', 'nomos_katoikias', 'tk_katoikias',
            'tilefono_oikias_1', 'tilefono_oikias_2', 'kinito_tilefono',
            # Business address
            'diefthinsi_epixeirisis', 'arithmos_epixeirisis', 'poli_epixeirisis',
            'dimos_epixeirisis', 'nomos_epixeirisis', 'tk_epixeirisis',
            'tilefono_epixeirisis_1', 'tilefono_epixeirisis_2', 'email',
            # Bank info
            'trapeza', 'iban',
            # Tax info
            'eidos_ipoxreou', 'katigoria_vivlion', 'nomiki_morfi',
            'agrotis', 'imerominia_enarksis',
            # Credentials
            'onoma_xristi_taxisnet', 'kodikos_taxisnet',
            'onoma_xristi_ika_ergodoti', 'kodikos_ika_ergodoti',
            'onoma_xristi_gemi', 'kodikos_gemi',
            # Related
            'afm_sizigou', 'afm_foreas', 'am_klidi',
            # Meta
            'is_active', 'created_at', 'updated_at',
            # Computed
            'obligations_count', 'documents_count', 'pending_obligations_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_obligations_count(self, obj):
        return obj.monthly_obligations.count()

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_pending_obligations_count(self, obj):
        return obj.monthly_obligations.filter(status='pending').count()


class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clients"""

    class Meta:
        model = ClientProfile
        fields = [
            # Basic info
            'afm', 'doy', 'eponimia', 'onoma', 'onoma_patros',
            # Identity
            'arithmos_taftotitas', 'eidos_taftotitas', 'prosopikos_arithmos',
            'amka', 'am_ika', 'arithmos_gemi', 'arithmos_dypa',
            # Personal dates
            'imerominia_gennisis', 'imerominia_gamou', 'filo',
            # Home address
            'diefthinsi_katoikias', 'arithmos_katoikias', 'poli_katoikias',
            'dimos_katoikias', 'nomos_katoikias', 'tk_katoikias',
            'tilefono_oikias_1', 'tilefono_oikias_2', 'kinito_tilefono',
            # Business address
            'diefthinsi_epixeirisis', 'arithmos_epixeirisis', 'poli_epixeirisis',
            'dimos_epixeirisis', 'nomos_epixeirisis', 'tk_epixeirisis',
            'tilefono_epixeirisis_1', 'tilefono_epixeirisis_2', 'email',
            # Bank info
            'trapeza', 'iban',
            # Tax info
            'eidos_ipoxreou', 'katigoria_vivlion', 'nomiki_morfi',
            'agrotis', 'imerominia_enarksis',
            # Credentials
            'onoma_xristi_taxisnet', 'kodikos_taxisnet',
            'onoma_xristi_ika_ergodoti', 'kodikos_ika_ergodoti',
            'onoma_xristi_gemi', 'kodikos_gemi',
            # Related
            'afm_sizigou', 'afm_foreas', 'am_klidi',
            # Status
            'is_active',
        ]

    def validate_afm(self, value):
        """Validate Greek AFM (Tax ID)"""
        if len(value) != 9 or not value.isdigit():
            raise serializers.ValidationError(
                "Το ΑΦΜ πρέπει να αποτελείται από 9 ψηφία."
            )
        # AFM checksum validation
        total = sum(int(value[i]) * (2 ** (8 - i)) for i in range(8))
        check_digit = (total % 11) % 10
        if check_digit != int(value[8]):
            raise serializers.ValidationError(
                "Μη έγκυρο ΑΦΜ - αποτυχία ελέγχου checksum."
            )
        return value


# Nested serializers for obligations/documents in client detail
class ClientObligationNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for client's obligations"""
    obligation_type_name = serializers.CharField(
        source='obligation_type.name', read_only=True
    )
    obligation_type_code = serializers.CharField(
        source='obligation_type.code', read_only=True
    )

    class Meta:
        model = MonthlyObligation
        fields = [
            'id', 'obligation_type', 'obligation_type_name', 'obligation_type_code',
            'year', 'month', 'deadline', 'status', 'completed_date', 'notes'
        ]


# ============================================
# CLIENT VIEWSET
# ============================================

class ClientViewSet(viewsets.ModelViewSet):
    """
    REST API ViewSet for ClientProfile

    Endpoints:
    - GET /api/clients/ - List all clients (with pagination, search, filters)
    - GET /api/clients/{id}/ - Get single client
    - POST /api/clients/ - Create client
    - PUT /api/clients/{id}/ - Update client
    - DELETE /api/clients/{id}/ - Delete client
    - GET /api/clients/{id}/obligations/ - Get client's obligations
    - GET /api/clients/{id}/documents/ - Get client's documents
    """
    queryset = ClientProfile.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = ClientPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ClientFilter
    ordering_fields = ['eponimia', 'afm', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ClientListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ClientCreateUpdateSerializer
        return ClientDetailSerializer

    def get_queryset(self):
        """Optimize queryset with counts for list view"""
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.annotate(
                _obligations_count=Count('monthly_obligations'),
                _documents_count=Count('documents')
            )
        return queryset

    @action(detail=True, methods=['get'])
    def obligations(self, request, pk=None):
        """
        GET /api/clients/{id}/obligations/
        Returns all obligations for a specific client
        """
        client = self.get_object()
        obligations = client.monthly_obligations.select_related(
            'obligation_type'
        ).order_by('-year', '-month')

        # Optional filtering
        status_filter = request.query_params.get('status')
        year_filter = request.query_params.get('year')
        month_filter = request.query_params.get('month')

        if status_filter:
            obligations = obligations.filter(status=status_filter)
        if year_filter:
            obligations = obligations.filter(year=year_filter)
        if month_filter:
            obligations = obligations.filter(month=month_filter)

        serializer = ClientObligationNestedSerializer(obligations, many=True)
        return Response({
            'client_id': client.id,
            'client_name': client.eponimia,
            'total_count': obligations.count(),
            'obligations': serializer.data
        })

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        GET /api/clients/{id}/documents/
        Returns all documents for a specific client
        """
        client = self.get_object()
        documents = client.documents.select_related(
            'obligation', 'obligation__obligation_type'
        ).order_by('-uploaded_at')

        # Optional filtering
        category = request.query_params.get('category')
        if category:
            documents = documents.filter(document_category=category)

        serializer = ClientDocumentSerializer(
            documents, many=True, context={'request': request}
        )
        return Response({
            'client_id': client.id,
            'client_name': client.eponimia,
            'total_count': documents.count(),
            'documents': serializer.data
        })
