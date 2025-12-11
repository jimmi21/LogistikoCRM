# -*- coding: utf-8 -*-
"""
accounting/api_reports.py
Author: Claude
Description: REST API views for Reports statistics and exports
"""

import csv
import io
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from datetime import timedelta
from calendar import monthrange

from .models import ClientProfile, MonthlyObligation, ObligationType

# Excel support - optional
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


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
    - type: clients, obligations, vat_summary, performance
    - format: csv, xlsx (default: xlsx)
    - period: same as reports_stats
    - download: true to trigger file download
    """
    export_type = request.query_params.get('type', 'clients')
    export_format = request.query_params.get('format', 'xlsx')
    period = request.query_params.get('period', 'month')
    download = request.query_params.get('download', 'false').lower() == 'true'

    # If not downloading, return metadata about available exports
    if not download:
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
                    'name': 'Σύνοψη ΦΠΑ',
                    'type': 'vat_summary',
                    'description': 'Αναλυτική κατάσταση ΦΠΑ ανά πελάτη',
                    'formats': ['csv', 'xlsx']
                },
                {
                    'name': 'Αναφορά απόδοσης',
                    'type': 'performance',
                    'description': 'Χρόνοι ολοκλήρωσης και KPIs',
                    'formats': ['csv', 'xlsx']
                }
            ],
            'current_request': {
                'type': export_type,
                'format': export_format,
                'period': period
            }
        })

    # Generate actual file download
    start_date, end_date = get_date_range(period)

    if export_type == 'clients':
        return export_clients(export_format)
    elif export_type == 'obligations':
        return export_obligations(export_format, start_date, end_date)
    elif export_type == 'vat_summary':
        return export_vat_summary(export_format, start_date, end_date)
    elif export_type == 'performance':
        return export_performance(export_format, start_date, end_date)
    else:
        return Response({'error': 'Μη έγκυρος τύπος αναφοράς'}, status=400)


def export_clients(export_format: str):
    """Export all active clients to CSV or Excel"""
    clients = ClientProfile.objects.filter(is_active=True).order_by('onoma')

    headers = ['ΑΦΜ', 'Επωνυμία', 'Email', 'Τηλέφωνο', 'ΔΟΥ', 'Διεύθυνση', 'Ημ/νία Εγγραφής']
    rows = []

    for client in clients:
        rows.append([
            client.afm or '',
            client.onoma or '',
            client.email or '',
            client.phone or '',
            client.doy or '',
            client.address or '',
            client.created_at.strftime('%d/%m/%Y') if client.created_at else '',
        ])

    filename = f'pelates_{timezone.now().strftime("%Y%m%d")}'
    return generate_export_file(headers, rows, filename, export_format, 'Πελάτες')


def export_obligations(export_format: str, start_date, end_date):
    """Export obligations to CSV or Excel"""
    obligations = MonthlyObligation.objects.select_related(
        'client', 'obligation_type'
    ).order_by('-deadline')

    if start_date and end_date:
        obligations = obligations.filter(
            Q(deadline__gte=start_date, deadline__lte=end_date) |
            Q(completed_date__gte=start_date, completed_date__lte=end_date)
        )

    headers = ['Πελάτης', 'ΑΦΜ', 'Τύπος', 'Περίοδος', 'Προθεσμία', 'Κατάσταση', 'Ημ/νία Ολοκλήρωσης', 'Σημειώσεις']
    rows = []

    status_labels = {
        'pending': 'Εκκρεμεί',
        'in_progress': 'Σε εξέλιξη',
        'completed': 'Ολοκληρώθηκε',
        'overdue': 'Εκπρόθεσμη',
        'cancelled': 'Ακυρώθηκε',
    }

    for obl in obligations:
        rows.append([
            obl.client.onoma if obl.client else '',
            obl.client.afm if obl.client else '',
            obl.obligation_type.name if obl.obligation_type else '',
            f'{obl.period_month}/{obl.period_year}' if obl.period_month and obl.period_year else '',
            obl.deadline.strftime('%d/%m/%Y') if obl.deadline else '',
            status_labels.get(obl.status, obl.status),
            obl.completed_date.strftime('%d/%m/%Y') if obl.completed_date else '',
            obl.notes or '',
        ])

    filename = f'ypoxreoseis_{timezone.now().strftime("%Y%m%d")}'
    return generate_export_file(headers, rows, filename, export_format, 'Υποχρεώσεις')


def export_vat_summary(export_format: str, start_date, end_date):
    """Export VAT summary by client"""
    # Get ΦΠΑ type obligations
    vat_obligations = MonthlyObligation.objects.filter(
        obligation_type__code='ΦΠΑ'
    ).select_related('client', 'obligation_type')

    if start_date and end_date:
        vat_obligations = vat_obligations.filter(
            Q(deadline__gte=start_date, deadline__lte=end_date) |
            Q(period_year=start_date.year)
        )

    headers = ['Πελάτης', 'ΑΦΜ', 'Περίοδος', 'Προθεσμία', 'Κατάσταση', 'Ημ/νία Ολοκλήρωσης']
    rows = []

    status_labels = {
        'pending': 'Εκκρεμεί',
        'in_progress': 'Σε εξέλιξη',
        'completed': 'Ολοκληρώθηκε',
        'overdue': 'Εκπρόθεσμη',
        'cancelled': 'Ακυρώθηκε',
    }

    for obl in vat_obligations.order_by('client__onoma', '-period_year', '-period_month'):
        rows.append([
            obl.client.onoma if obl.client else '',
            obl.client.afm if obl.client else '',
            f'{obl.period_month}/{obl.period_year}' if obl.period_month and obl.period_year else '',
            obl.deadline.strftime('%d/%m/%Y') if obl.deadline else '',
            status_labels.get(obl.status, obl.status),
            obl.completed_date.strftime('%d/%m/%Y') if obl.completed_date else '',
        ])

    filename = f'fpa_synopsi_{timezone.now().strftime("%Y%m%d")}'
    return generate_export_file(headers, rows, filename, export_format, 'Σύνοψη ΦΠΑ')


def export_performance(export_format: str, start_date, end_date):
    """Export performance KPIs"""
    today = timezone.now().date()

    # Aggregate stats per client
    clients = ClientProfile.objects.filter(is_active=True).annotate(
        total_obligations=Count('monthlyobligation'),
        completed=Count('monthlyobligation', filter=Q(monthlyobligation__status='completed')),
        pending=Count('monthlyobligation', filter=Q(monthlyobligation__status='pending')),
        overdue=Count('monthlyobligation', filter=Q(
            Q(monthlyobligation__status='overdue') |
            Q(monthlyobligation__status='pending', monthlyobligation__deadline__lt=today)
        )),
    ).order_by('onoma')

    headers = ['Πελάτης', 'ΑΦΜ', 'Σύνολο Υποχρεώσεων', 'Ολοκληρωμένες', 'Εκκρεμείς', 'Εκπρόθεσμες', 'Ποσοστό Ολοκλήρωσης']
    rows = []

    for client in clients:
        completion_rate = round(
            (client.completed / client.total_obligations * 100) if client.total_obligations > 0 else 0,
            1
        )
        rows.append([
            client.onoma or '',
            client.afm or '',
            client.total_obligations,
            client.completed,
            client.pending,
            client.overdue,
            f'{completion_rate}%',
        ])

    filename = f'apodosi_{timezone.now().strftime("%Y%m%d")}'
    return generate_export_file(headers, rows, filename, export_format, 'Απόδοση')


def generate_export_file(headers: list, rows: list, filename: str, export_format: str, sheet_name: str = 'Data'):
    """Generate CSV or Excel file from headers and rows"""
    if export_format == 'csv':
        return generate_csv(headers, rows, filename)
    elif export_format == 'xlsx' and HAS_OPENPYXL:
        return generate_xlsx(headers, rows, filename, sheet_name)
    else:
        # Fallback to CSV if xlsx not available
        return generate_csv(headers, rows, filename)


def generate_csv(headers: list, rows: list, filename: str):
    """Generate CSV file response"""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    writer.writerows(rows)

    response = HttpResponse(
        output.getvalue().encode('utf-8-sig'),  # BOM for Excel compatibility
        content_type='text/csv; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response


def generate_xlsx(headers: list, rows: list, filename: str, sheet_name: str):
    """Generate Excel file response"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    # Header styling
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center')
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Write data rows
    for row_num, row_data in enumerate(rows, 2):
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(vertical='center')

    # Auto-adjust column widths
    for col_num, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        max_length = len(str(header))
        for row in rows:
            if col_num <= len(row):
                cell_length = len(str(row[col_num - 1]))
                if cell_length > max_length:
                    max_length = cell_length
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Freeze header row
    ws.freeze_panes = 'A2'

    # Generate response
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_statement(request, client_id: int):
    """
    GET /api/reports/client-statement/{client_id}/

    Generate a statement for a specific client showing all their obligations.
    Parameters:
    - format: csv, xlsx (default: xlsx)
    - year: Filter by year (optional)
    """
    export_format = request.query_params.get('format', 'xlsx')
    year = request.query_params.get('year')

    try:
        client = ClientProfile.objects.get(pk=client_id)
    except ClientProfile.DoesNotExist:
        return Response({'error': 'Ο πελάτης δεν βρέθηκε'}, status=404)

    obligations = MonthlyObligation.objects.filter(
        client=client
    ).select_related('obligation_type').order_by('-period_year', '-period_month')

    if year:
        obligations = obligations.filter(period_year=int(year))

    headers = ['Τύπος', 'Περίοδος', 'Προθεσμία', 'Κατάσταση', 'Ημ/νία Ολοκλήρωσης', 'Σημειώσεις']
    rows = []

    status_labels = {
        'pending': 'Εκκρεμεί',
        'in_progress': 'Σε εξέλιξη',
        'completed': 'Ολοκληρώθηκε',
        'overdue': 'Εκπρόθεσμη',
        'cancelled': 'Ακυρώθηκε',
    }

    for obl in obligations:
        rows.append([
            obl.obligation_type.name if obl.obligation_type else '',
            f'{obl.period_month}/{obl.period_year}' if obl.period_month and obl.period_year else '',
            obl.deadline.strftime('%d/%m/%Y') if obl.deadline else '',
            status_labels.get(obl.status, obl.status),
            obl.completed_date.strftime('%d/%m/%Y') if obl.completed_date else '',
            obl.notes or '',
        ])

    # Clean filename from client name
    safe_name = ''.join(c if c.isalnum() else '_' for c in (client.onoma or 'client'))
    filename = f'kartela_{safe_name}_{timezone.now().strftime("%Y%m%d")}'
    sheet_name = f'Καρτέλα {client.afm}'

    return generate_export_file(headers, rows, filename, export_format, sheet_name)
