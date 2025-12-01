"""
Context processor για admin dashboard statistics
Παρέχει real-time stats για την accounting dashboard
"""
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from accounting.models import MonthlyObligation


def dashboard_stats(request):
    """
    Προσθέτει accounting statistics στο admin context

    Returns dashboard stats:
    - pending_count: Εκκρεμείς υποχρεώσεις
    - overdue_count: Καθυστερημένες
    - completed_this_month: Ολοκληρωμένες τον τρέχοντα μήνα
    - total_revenue: Συνολικά έσοδα μήνα
    """
    if not request.path.startswith('/admin/'):
        return {}

    now = timezone.now()
    today = now.date()
    first_of_month = today.replace(day=1)

    # Εκκρεμείς υποχρεώσεις
    pending_count = MonthlyObligation.objects.filter(
        status='pending'
    ).count()

    # Καθυστερημένες (pending + deadline παρελθόν)
    overdue_count = MonthlyObligation.objects.filter(
        status='pending',
        deadline__lt=today
    ).count()

    # Ολοκληρωμένες τον τρέχοντα μήνα
    completed_this_month = MonthlyObligation.objects.filter(
        status='completed',
        completed_date__gte=first_of_month
    ).count()

    # Συνολικά έσοδα μήνα (completed obligations)
    revenue_data = MonthlyObligation.objects.filter(
        status='completed',
        completed_date__gte=first_of_month
    ).aggregate(
        total=Sum('cost')
    )
    total_revenue = revenue_data['total'] or 0

    return {
        'stats': {
            'pending_count': pending_count,
            'overdue_count': overdue_count,
            'completed_this_month': completed_this_month,
            'total_revenue': f'{total_revenue:.2f}',
        },
        'today': today,
    }
