# mydata/views.py
"""
Django REST Framework Views για myDATA module.

Παρέχει API endpoints για:
- VAT Records (list, detail, summaries)
- Credentials management
- Sync operations
- Dashboard data
"""

from datetime import date, timedelta
from decimal import Decimal
import logging

from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.models import ClientProfile
from .models import MyDataCredentials, VATRecord, VATSyncLog
from .serializers import (
    MyDataCredentialsSerializer,
    CredentialsUpdateSerializer,
    VATRecordSerializer,
    VATRecordListSerializer,
    VATSyncLogSerializer,
    VATPeriodSummarySerializer,
    VATCategoryBreakdownSerializer,
    ClientVATSummarySerializer,
)

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_vat_rate_for_category(category: int) -> int:
    """Get VAT rate percentage for category."""
    rates = {1: 24, 2: 13, 3: 6, 4: 17, 5: 9, 6: 4, 7: 0, 8: 0}
    return rates.get(category, 0)


def get_vat_rate_display(category: int) -> str:
    """Get VAT rate display string."""
    rate = get_vat_rate_for_category(category)
    return f"{rate}%" if category < 8 else "Χωρίς ΦΠΑ"


def build_period_summary(client, year: int, month: int) -> dict:
    """Build complete period summary for a client."""
    income = VATRecord.get_period_summary(client, year, month, rec_type=1)
    expense = VATRecord.get_period_summary(client, year, month, rec_type=2)

    return {
        'year': year,
        'month': month,
        'income_net': income['net_value'],
        'income_vat': income['vat_amount'],
        'income_gross': income['gross_value'],
        'income_count': income['count'],
        'expense_net': expense['net_value'],
        'expense_vat': expense['vat_amount'],
        'expense_gross': expense['gross_value'],
        'expense_count': expense['count'],
        'net_difference': income['net_value'] - expense['net_value'],
        'vat_difference': income['vat_amount'] - expense['vat_amount'],
    }


def build_category_breakdown(client, year: int, month: int, rec_type: int) -> list:
    """Build VAT category breakdown for a period."""
    breakdown = VATRecord.get_period_by_category(client, year, month, rec_type)

    return [
        {
            'vat_category': item['vat_category'],
            'vat_rate': get_vat_rate_for_category(item['vat_category']),
            'vat_rate_display': get_vat_rate_display(item['vat_category']),
            'net_value': item['total_net'] or Decimal('0.00'),
            'vat_amount': item['total_vat'] or Decimal('0.00'),
            'count': item['record_count'] or 0,
        }
        for item in breakdown
    ]


# =============================================================================
# CREDENTIALS VIEWSET
# =============================================================================

class MyDataCredentialsViewSet(viewsets.ModelViewSet):
    """
    ViewSet για MyDataCredentials.

    Endpoints:
    - GET /api/mydata/credentials/ - List all
    - GET /api/mydata/credentials/{id}/ - Detail
    - POST /api/mydata/credentials/ - Create
    - PUT /api/mydata/credentials/{id}/ - Update
    - DELETE /api/mydata/credentials/{id}/ - Delete
    - POST /api/mydata/credentials/{id}/verify/ - Verify credentials
    - POST /api/mydata/credentials/{id}/update_credentials/ - Update secret keys
    - POST /api/mydata/credentials/{id}/sync/ - Trigger sync
    """

    queryset = MyDataCredentials.objects.select_related('client').all()
    serializer_class = MyDataCredentialsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter by client if specified."""
        queryset = super().get_queryset()

        # Filter by client AFM
        afm = self.request.query_params.get('afm')
        if afm:
            queryset = queryset.filter(client__afm=afm)

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by verified status
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')

        return queryset

    @action(detail=False, methods=['get'], url_path='by-client/(?P<client_id>[^/.]+)')
    def by_client(self, request, client_id=None):
        """
        Get credentials for a specific client by client ID.

        GET /api/mydata/credentials/by-client/{client_id}/
        """
        try:
            credentials = MyDataCredentials.objects.select_related('client').get(
                client_id=client_id,
                is_active=True
            )
            serializer = self.get_serializer(credentials)
            return Response(serializer.data)
        except MyDataCredentials.DoesNotExist:
            return Response(
                {'error': 'Δεν βρέθηκαν credentials για αυτόν τον πελάτη'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify credentials by making a test API call."""
        credentials = self.get_object()

        if not credentials.has_credentials:
            return Response(
                {'error': 'Δεν έχουν οριστεί credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = credentials.verify_credentials()

        return Response({
            'success': success,
            'is_verified': credentials.is_verified,
            'error': credentials.verification_error if not success else None,
        })

    @action(detail=True, methods=['post'])
    def update_credentials(self, request, pk=None):
        """Update the encrypted credentials."""
        credentials = self.get_object()
        serializer = CredentialsUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Set new credentials (will be encrypted automatically)
        credentials.user_id = serializer.validated_data['user_id']
        credentials.subscription_key = serializer.validated_data['subscription_key']
        credentials.is_sandbox = serializer.validated_data.get('is_sandbox', False)
        credentials.save()

        return Response({
            'success': True,
            'message': 'Τα credentials ενημερώθηκαν. Κάντε verify για επιβεβαίωση.',
        })

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Trigger VAT sync for this client."""
        from django.core.management import call_command
        from io import StringIO

        credentials = self.get_object()

        if not credentials.has_credentials:
            return Response(
                {'error': 'Δεν έχουν οριστεί credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not credentials.is_active:
            return Response(
                {'error': 'Τα credentials είναι απενεργοποιημένα'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get sync parameters
        days = request.data.get('days', 30)
        year = request.data.get('year')
        month = request.data.get('month')

        try:
            out = StringIO()
            args = ['--client', credentials.client.afm]

            if year and month:
                args.extend(['--year', str(year), '--month', str(month)])
            else:
                args.extend(['--days', str(days)])

            call_command('mydata_sync_vat', *args, stdout=out)

            return Response({
                'success': True,
                'message': out.getvalue(),
            })

        except Exception as e:
            logger.error(f"Sync error for {credentials.client.afm}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# VAT RECORD VIEWSET
# =============================================================================

class VATRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet για VATRecord (read-only).

    Endpoints:
    - GET /api/mydata/records/ - List records
    - GET /api/mydata/records/{id}/ - Record detail
    - GET /api/mydata/records/summary/ - Period summary
    - GET /api/mydata/records/by_category/ - Category breakdown
    """

    queryset = VATRecord.objects.select_related('client').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return VATRecordListSerializer
        return VATRecordSerializer

    def get_queryset(self):
        """Apply filters."""
        queryset = super().get_queryset()

        # Filter by client
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        afm = self.request.query_params.get('afm')
        if afm:
            queryset = queryset.filter(client__afm=afm)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(issue_date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(issue_date__lte=date_to)

        # Filter by year/month
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(issue_date__year=int(year))

        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(issue_date__month=int(month))

        # Filter by rec_type (1=income, 2=expense)
        rec_type = self.request.query_params.get('rec_type')
        if rec_type:
            queryset = queryset.filter(rec_type=int(rec_type))

        # Filter by VAT category
        vat_category = self.request.query_params.get('vat_category')
        if vat_category:
            queryset = queryset.filter(vat_category=int(vat_category))

        # Exclude cancelled by default
        include_cancelled = self.request.query_params.get('include_cancelled', 'false')
        if include_cancelled.lower() != 'true':
            queryset = queryset.filter(is_cancelled=False)

        return queryset.order_by('-issue_date', '-mark')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get period summary.

        Query params:
        - afm: Client AFM (required)
        - year: Year (default: current)
        - month: Month (default: current)
        """
        afm = request.query_params.get('afm')
        if not afm:
            return Response(
                {'error': 'Απαιτείται AFM πελάτη'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = ClientProfile.objects.get(afm=afm)
        except ClientProfile.DoesNotExist:
            return Response(
                {'error': 'Δεν βρέθηκε πελάτης'},
                status=status.HTTP_404_NOT_FOUND
            )

        today = date.today()
        year = int(request.query_params.get('year', today.year))
        month = int(request.query_params.get('month', today.month))

        summary = build_period_summary(client, year, month)
        serializer = VATPeriodSummarySerializer(summary)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get breakdown by VAT category.

        Query params:
        - afm: Client AFM (required)
        - year: Year (default: current)
        - month: Month (default: current)
        - rec_type: 1=income, 2=expense (optional, returns both if not specified)
        """
        afm = request.query_params.get('afm')
        if not afm:
            return Response(
                {'error': 'Απαιτείται AFM πελάτη'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = ClientProfile.objects.get(afm=afm)
        except ClientProfile.DoesNotExist:
            return Response(
                {'error': 'Δεν βρέθηκε πελάτης'},
                status=status.HTTP_404_NOT_FOUND
            )

        today = date.today()
        year = int(request.query_params.get('year', today.year))
        month = int(request.query_params.get('month', today.month))
        rec_type = request.query_params.get('rec_type')

        if rec_type:
            breakdown = build_category_breakdown(client, year, month, int(rec_type))
            serializer = VATCategoryBreakdownSerializer(breakdown, many=True)
            return Response(serializer.data)

        # Return both income and expense
        income_breakdown = build_category_breakdown(client, year, month, 1)
        expense_breakdown = build_category_breakdown(client, year, month, 2)

        return Response({
            'income': VATCategoryBreakdownSerializer(income_breakdown, many=True).data,
            'expense': VATCategoryBreakdownSerializer(expense_breakdown, many=True).data,
        })


# =============================================================================
# SYNC LOG VIEWSET
# =============================================================================

class VATSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet για VATSyncLog (read-only).

    Endpoints:
    - GET /api/mydata/logs/ - List logs
    - GET /api/mydata/logs/{id}/ - Log detail
    """

    queryset = VATSyncLog.objects.select_related('client').all()
    serializer_class = VATSyncLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Apply filters."""
        queryset = super().get_queryset()

        # Filter by client
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        afm = self.request.query_params.get('afm')
        if afm:
            queryset = queryset.filter(client__afm=afm)

        # Filter by sync type
        sync_type = self.request.query_params.get('sync_type')
        if sync_type:
            queryset = queryset.filter(sync_type=sync_type.upper())

        # Filter by status
        log_status = self.request.query_params.get('status')
        if log_status:
            queryset = queryset.filter(status=log_status.upper())

        # Limit results
        limit = self.request.query_params.get('limit', 50)
        queryset = queryset[:int(limit)]

        return queryset


# =============================================================================
# DASHBOARD API VIEW
# =============================================================================

class MyDataDashboardView(APIView):
    """
    Dashboard endpoint για myDATA overview.

    GET /api/mydata/dashboard/
    Returns aggregated data for all clients.

    Query params:
    - year: Year (default: current)
    - month: Month (default: current)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        year = int(request.query_params.get('year', today.year))
        month = int(request.query_params.get('month', today.month))

        # Get all clients with mydata credentials
        credentials_qs = MyDataCredentials.objects.select_related('client').all()

        total_clients = ClientProfile.objects.count()
        clients_with_credentials = credentials_qs.count()
        verified_credentials = credentials_qs.filter(is_verified=True).count()

        # Aggregate totals for the period
        period_records = VATRecord.objects.filter(
            issue_date__year=year,
            issue_date__month=month,
            is_cancelled=False
        )

        income_totals = period_records.filter(rec_type=1).aggregate(
            total_net=Sum('net_value'),
            total_vat=Sum('vat_amount'),
        )

        expense_totals = period_records.filter(rec_type=2).aggregate(
            total_net=Sum('net_value'),
            total_vat=Sum('vat_amount'),
        )

        # Per-client summaries
        clients_data = []
        for creds in credentials_qs:
            client = creds.client
            summary = build_period_summary(client, year, month)
            income_breakdown = build_category_breakdown(client, year, month, 1)
            expense_breakdown = build_category_breakdown(client, year, month, 2)

            clients_data.append({
                'client_afm': client.afm,
                'client_name': client.eponimia,
                'has_credentials': creds.has_credentials,
                'is_verified': creds.is_verified,
                'last_sync': creds.last_vat_sync_at,
                'current_period': summary,
                'income_by_category': income_breakdown,
                'expense_by_category': expense_breakdown,
            })

        return Response({
            'period': {
                'year': year,
                'month': month,
            },
            'overview': {
                'total_clients': total_clients,
                'clients_with_credentials': clients_with_credentials,
                'verified_credentials': verified_credentials,
                'total_income_net': income_totals['total_net'] or Decimal('0.00'),
                'total_income_vat': income_totals['total_vat'] or Decimal('0.00'),
                'total_expense_net': expense_totals['total_net'] or Decimal('0.00'),
                'total_expense_vat': expense_totals['total_vat'] or Decimal('0.00'),
            },
            'clients': clients_data,
        })


# =============================================================================
# CLIENT VAT DETAIL VIEW
# =============================================================================

class ClientVATDetailView(APIView):
    """
    Detailed VAT view for a single client.

    GET /api/mydata/client/{afm}/
    Returns complete VAT data for a client.

    Query params:
    - year: Year (default: current)
    - month: Month (default: current)
    - include_records: Include individual records (default: false)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, afm):
        try:
            client = ClientProfile.objects.get(afm=afm)
        except ClientProfile.DoesNotExist:
            return Response(
                {'error': 'Δεν βρέθηκε πελάτης'},
                status=status.HTTP_404_NOT_FOUND
            )

        today = date.today()
        year = int(request.query_params.get('year', today.year))
        month = int(request.query_params.get('month', today.month))
        include_records = request.query_params.get('include_records', 'false').lower() == 'true'

        # Check for credentials
        try:
            credentials = client.mydata_credentials
            has_credentials = credentials.has_credentials
            is_verified = credentials.is_verified
            last_sync = credentials.last_vat_sync_at
        except MyDataCredentials.DoesNotExist:
            has_credentials = False
            is_verified = False
            last_sync = None

        # Build response
        summary = build_period_summary(client, year, month)
        income_breakdown = build_category_breakdown(client, year, month, 1)
        expense_breakdown = build_category_breakdown(client, year, month, 2)

        response_data = {
            'client': {
                'afm': client.afm,
                'name': client.eponimia,
            },
            'credentials': {
                'has_credentials': has_credentials,
                'is_verified': is_verified,
                'last_sync': last_sync,
            },
            'period': {
                'year': year,
                'month': month,
            },
            'summary': summary,
            'income_by_category': income_breakdown,
            'expense_by_category': expense_breakdown,
        }

        if include_records:
            records = VATRecord.objects.filter(
                client=client,
                issue_date__year=year,
                issue_date__month=month,
                is_cancelled=False,
            ).order_by('-issue_date', '-mark')

            response_data['records'] = VATRecordListSerializer(records, many=True).data

        return Response(response_data)


# =============================================================================
# MONTHLY TREND VIEW
# =============================================================================

class MonthlyTrendView(APIView):
    """
    Monthly trend data for charts.

    GET /api/mydata/trend/
    Returns VAT data for the last N months.

    Query params:
    - afm: Client AFM (optional, returns all if not specified)
    - months: Number of months to include (default: 6)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        afm = request.query_params.get('afm')
        months_count = int(request.query_params.get('months', 6))

        # Build list of months
        today = date.today()
        months = []
        current = today.replace(day=1)

        for _ in range(months_count):
            months.append((current.year, current.month))
            # Go to previous month
            if current.month == 1:
                current = current.replace(year=current.year - 1, month=12)
            else:
                current = current.replace(month=current.month - 1)

        months.reverse()  # Oldest first

        # Build queryset filter
        base_qs = VATRecord.objects.filter(is_cancelled=False)
        if afm:
            base_qs = base_qs.filter(client__afm=afm)

        # Collect data for each month
        trend_data = []
        for year, month in months:
            income = base_qs.filter(
                issue_date__year=year,
                issue_date__month=month,
                rec_type=1
            ).aggregate(
                net=Sum('net_value'),
                vat=Sum('vat_amount'),
                count=Count('id')
            )

            expense = base_qs.filter(
                issue_date__year=year,
                issue_date__month=month,
                rec_type=2
            ).aggregate(
                net=Sum('net_value'),
                vat=Sum('vat_amount'),
                count=Count('id')
            )

            trend_data.append({
                'year': year,
                'month': month,
                'month_name': self._get_month_name(month),
                'income_net': income['net'] or Decimal('0.00'),
                'income_vat': income['vat'] or Decimal('0.00'),
                'income_count': income['count'] or 0,
                'expense_net': expense['net'] or Decimal('0.00'),
                'expense_vat': expense['vat'] or Decimal('0.00'),
                'expense_count': expense['count'] or 0,
                'vat_balance': (income['vat'] or Decimal('0.00')) - (expense['vat'] or Decimal('0.00')),
            })

        return Response({
            'afm': afm,
            'months_count': months_count,
            'data': trend_data,
        })

    def _get_month_name(self, month: int) -> str:
        """Get Greek month abbreviation."""
        names = {
            1: 'Ιαν', 2: 'Φεβ', 3: 'Μαρ', 4: 'Απρ',
            5: 'Μάι', 6: 'Ιουν', 7: 'Ιουλ', 8: 'Αυγ',
            9: 'Σεπ', 10: 'Οκτ', 11: 'Νοε', 12: 'Δεκ'
        }
        return names.get(month, str(month))
