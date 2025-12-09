# -*- coding: utf-8 -*-
"""
accounting/api_reports.py
Author: Claude
Description: REST API views for Reports statistics
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from datetime import timedelta
from calendar import monthrange

from .models import ClientProfile, MonthlyObligation


def get_date_range(period: str):
    """
    Returns start_date and end_date based on period filter.
    Periods: today, week, month, quarter, year, all
    """
    today = timezone.now().date()

    if period == 'today':
        return today, today
    elif period == 'week':
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week, today
    elif period == 'month':
        start_of_month = today.replace(day=1)
        return start_of_month, today
    elif period == 'quarter':
        current_quarter = (today.month - 1) // 3
        start_month = current_quarter * 3 + 1
        start_of_quarter = today.replace(month=start_month, day=1)
        return start_of_quarter, today
    elif period == 'year':
        start_of_year = today.replace(month=1, day=1)
        return start_of_year, today
    else:  # 'all' or any other value
        return None, None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_stats(request):
    """
    GET /api/reports/stats/

    Returns comprehensive statistics for the Reports page.
    Parameters:
    - period: today, week, month, quarter, year, all (default: month)

    Returns:
    - total_clients: Total active clients
    - completed_obligations: Completed obligations in period
    - pending_obligations: Currently pending obligations
    - overdue_obligations: Currently overdue obligations
    - obligations_by_type: Breakdown by obligation type
    - monthly_activity: Monthly completion counts (last 12 months)
    - completion_rate: Percentage of completed vs total
    - comparison: Trend compared to previous period
    """
    period = request.query_params.get('period', 'month')
    today = timezone.now().date()

    # Get date range based on period
    start_date, end_date = get_date_range(period)

    # Total active clients
    total_clients = ClientProfile.objects.filter(is_active=True).count()

    # Base querysets
    all_obligations = MonthlyObligation.objects.all()

    # Completed in period
    completed_qs = all_obligations.filter(status='completed')
    if start_date and end_date:
        completed_qs = completed_qs.filter(
            completed_date__gte=start_date,
            completed_date__lte=end_date
        )
    completed_obligations = completed_qs.count()

    # Pending (current)
    pending_obligations = all_obligations.filter(status='pending').count()

    # Overdue (current - includes pending past deadline)
    overdue_obligations = all_obligations.filter(
        Q(status='overdue') | Q(status='pending', deadline__lt=today)
    ).count()

    # Obligations by type (all time or in period)
    if start_date and end_date:
        type_qs = all_obligations.filter(
            Q(created_at__date__gte=start_date) |
            Q(deadline__gte=start_date, deadline__lte=end_date)
        )
    else:
        type_qs = all_obligations

    obligations_by_type = list(
        type_qs.values('obligation_type__name', 'obligation_type__code')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Monthly activity (last 12 months)
    twelve_months_ago = today.replace(day=1) - timedelta(days=365)
    monthly_activity = list(
        all_obligations.filter(
            status='completed',
            completed_date__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('completed_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
    )

    # Format monthly activity for frontend
    monthly_data = []
    greek_months = ['Ιαν', 'Φεβ', 'Μαρ', 'Απρ', 'Μαι', 'Ιουν',
                    'Ιουλ', 'Αυγ', 'Σεπ', 'Οκτ', 'Νοε', 'Δεκ']

    for item in monthly_activity:
        if item['month']:
            month_idx = item['month'].month - 1
            monthly_data.append({
                'month': greek_months[month_idx],
                'month_num': item['month'].month,
                'year': item['month'].year,
                'count': item['count']
            })

    # Fill in missing months with zero
    current_month = today.replace(day=1)
    all_months = []
    for i in range(12):
        month_date = current_month - timedelta(days=30*i)
        month_date = month_date.replace(day=1)
        month_idx = month_date.month - 1

        existing = next(
            (m for m in monthly_data
             if m['month_num'] == month_date.month and m['year'] == month_date.year),
            None
        )

        all_months.append({
            'month': greek_months[month_idx],
            'month_num': month_date.month,
            'year': month_date.year,
            'count': existing['count'] if existing else 0
        })

    all_months.reverse()

    # Completion rate
    total_in_period = completed_obligations + pending_obligations + overdue_obligations
    completion_rate = round(
        (completed_obligations / total_in_period * 100) if total_in_period > 0 else 0,
        1
    )

    # Comparison with previous period (for trend indicators)
    comparison = calculate_comparison(period, start_date, end_date)

    return Response({
        'period': period,
        'total_clients': total_clients,
        'completed_obligations': completed_obligations,
        'pending_obligations': pending_obligations,
        'overdue_obligations': overdue_obligations,
        'obligations_by_type': obligations_by_type,
        'monthly_activity': all_months,
        'completion_rate': completion_rate,
        'comparison': comparison,
        'generated_at': timezone.now().isoformat()
    })


def calculate_comparison(period: str, current_start, current_end):
    """
    Calculate comparison with previous period for trend indicators.
    """
    today = timezone.now().date()

    if period == 'today':
        prev_start = prev_end = today - timedelta(days=1)
    elif period == 'week':
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=6)
    elif period == 'month':
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end.replace(day=1)
    elif period == 'quarter':
        prev_end = current_start - timedelta(days=1)
        prev_quarter = (prev_end.month - 1) // 3
        prev_start_month = prev_quarter * 3 + 1
        prev_start = prev_end.replace(month=prev_start_month, day=1)
    elif period == 'year':
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end.replace(month=1, day=1)
    else:
        return {'clients': 0, 'completed': 0, 'pending': 0, 'overdue': 0}

    # Previous period stats
    prev_completed = MonthlyObligation.objects.filter(
        status='completed',
        completed_date__gte=prev_start,
        completed_date__lte=prev_end
    ).count()

    # Current period stats (for comparison calculation)
    curr_completed = MonthlyObligation.objects.filter(
        status='completed',
        completed_date__gte=current_start,
        completed_date__lte=current_end
    ).count() if current_start and current_end else 0

    # Calculate percentage changes
    def calc_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round((current - previous) / previous * 100, 1)

    # Client comparison - new clients in period
    new_clients_current = ClientProfile.objects.filter(
        created_at__date__gte=current_start,
        created_at__date__lte=current_end
    ).count() if current_start and current_end else 0

    new_clients_prev = ClientProfile.objects.filter(
        created_at__date__gte=prev_start,
        created_at__date__lte=prev_end
    ).count()

    return {
        'clients_change': calc_change(new_clients_current, new_clients_prev),
        'completed_change': calc_change(curr_completed, prev_completed),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_export(request):
    """
    GET /api/reports/export/

    Export reports data for download.
    Parameters:
    - type: clients, obligations, summary
    - format: csv, xlsx, pdf (default: csv)
    - period: same as reports_stats

    Currently returns metadata for the frontend to handle export.
    """
    export_type = request.query_params.get('type', 'summary')
    export_format = request.query_params.get('format', 'csv')
    period = request.query_params.get('period', 'month')

    # For now, return info about available exports
    # Actual file generation can be added later
    return Response({
        'available_exports': [
            {
                'name': 'Αναφορά πελατών',
                'type': 'clients',
                'description': 'Πλήρης λίστα πελατών με στοιχεία επικοινωνίας',
                'formats': ['csv', 'xlsx']
            },
            {
                'name': 'Αναφορά υποχρεώσεων',
                'type': 'obligations',
                'description': 'Κατάσταση υποχρεώσεων ανά μήνα',
                'formats': ['csv', 'xlsx']
            },
            {
                'name': 'Οικονομική αναφορά',
                'type': 'financial',
                'description': 'Έσοδα και στατιστικά χρεώσεων',
                'formats': ['csv', 'xlsx', 'pdf']
            },
            {
                'name': 'Αναφορά απόδοσης',
                'type': 'performance',
                'description': 'Χρόνοι ολοκλήρωσης και KPIs',
                'formats': ['csv', 'xlsx', 'pdf']
            }
        ],
        'current_request': {
            'type': export_type,
            'format': export_format,
            'period': period
        }
    })
