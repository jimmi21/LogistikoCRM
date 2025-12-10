"""
Accounting Views - Complete Professional Implementation
Author: ddiplas
Version: 2.0
Description: Comprehensive views for accounting management system with advanced features
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q, Sum, Avg
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.middleware.csrf import get_token
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import ListView
from django.views.decorators.http import require_GET

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsVoIPMonitor, IsLocalRequest

from .models import (
    ClientProfile, ClientObligation, MonthlyObligation,
    ObligationType, VoIPCall, VoIPCallLog, EmailTemplate, EmailLog,
    Ticket, ClientDocument, ScheduledEmail
)
from django.utils.html import strip_tags 
from .serializers import VoIPCallSerializer, ClientDocumentSerializer, VoIPCallLogSerializer 

from datetime import timedelta, datetime
from collections import defaultdict
import logging
import json
import traceback
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
import csv

# SECURITY: File upload validation
from common.utils.file_validation import validate_file_upload
from django.core.exceptions import ValidationError as DjangoValidationError

# Helper functions for views
from .views.helpers import (
    _safe_int,
    _calculate_dashboard_stats,
    _build_filtered_query,
    _calculate_monthly_stats,
    _process_individual_obligations,
    _process_grouped_obligations,
    _match_client_by_phone_standalone,
    _format_voip_call,
    _get_status_color,
    _get_resolution_color,
    _calculate_success_rate,
    _log_voip_change,
    _calculate_send_time,
    _create_bulk_emails,
    _get_filters_from_request,
    _build_export_query,
    _apply_excel_styling,
    _write_excel_headers,
    _write_excel_data,
    _auto_adjust_excel_columns,
    _calculate_monthly_completion_stats,
    _calculate_client_performance,
    _calculate_time_stats,
    _calculate_revenue,
    _calculate_type_stats,
    _calculate_current_month_stats,
    _format_chart_data,
)

# VoIP views (extracted to separate module)
from .views.voip import (
    voip_dashboard,
    fritz_webhook,
    voip_calls_api,
    voip_call_update,
    voip_statistics,
    voip_bulk_action,
    voip_export_csv,
    VoIPCallViewSet,
    VoIPCallsListView,
    VoIPCallLogViewSet,
)

# Dashboard views (extracted to separate module)
from .views.dashboard import (
    dashboard_view,
    reports_view,
)

# Calendar views (extracted to separate module)
from .views.calendar import (
    calendar_view,
    calendar_events_api,
)

# Email views (extracted to separate module)
from .views.email_views import (
    api_email_templates,
    api_send_bulk_email,
    api_email_template_detail,
    api_send_bulk_email_direct,
    send_ticket_email,
)

# Obligation views (extracted to separate module)
from .views.obligations import (
    quick_complete_obligation,
    bulk_complete_view,
    advanced_bulk_complete,
    check_obligation_duplicate,
    complete_with_file,
    bulk_complete_obligations,
    obligation_detail_view,
    api_obligations_wizard,
    wizard_bulk_process,
)

# ============================================
# LOGGER CONFIGURATION
# ============================================
logger = logging.getLogger(__name__)

# ============================================
# DASHBOARD VIEWS - Extracted to views/dashboard.py
# ============================================
# Dashboard views have been moved to accounting/views/dashboard.py
# They are imported at the top of this file from .views.dashboard


# ============================================
# CLIENT DETAIL VIEW
# ============================================

@staff_member_required
def client_detail_view(request, client_id):
    """
    Comprehensive client view with all obligations and analytics
    """
    client = get_object_or_404(ClientProfile, id=client_id)
    now = timezone.now()
    
    # All obligations for this client
    all_obligations = MonthlyObligation.objects.filter(
        client=client
    ).select_related('obligation_type').order_by('-deadline')
    
    # Calculate statistics
    stats = {
        'total': all_obligations.count(),
        'pending': all_obligations.filter(status='pending').count(),
        'completed': all_obligations.filter(status='completed').count(),
        'overdue': all_obligations.filter(status='overdue').count(),
    }
    
    # Upcoming obligations (next 30 days)
    next_month = now.date() + timedelta(days=30)
    upcoming = all_obligations.filter(
        deadline__range=[now.date(), next_month],
        status='pending'
    ).order_by('deadline')[:10]
    
    # Overdue obligations
    overdue = all_obligations.filter(
        deadline__lt=now.date(),
        status__in=['pending', 'overdue']
    ).order_by('deadline')
    
    # Recent completed (last 30 days)
    past_month = now.date() - timedelta(days=30)
    recent_completed = all_obligations.filter(
        status='completed',
        completed_date__gte=past_month
    ).order_by('-completed_date')[:10]
    
    # Monthly breakdown (last 6 months)
    monthly_stats = _calculate_monthly_stats(all_obligations, now)
    
    # Active obligation types
    active_types = ClientObligation.objects.filter(
        client=client,
        is_active=True
    ).select_related('obligation_type')
    
    # Client documents
    documents = ClientDocument.objects.filter(
        client=client
    ).order_by('-uploaded_at')
    
    context = {
        'title': f'{client.eponimia} - Λεπτομέρειες',
        'client': client,
        'stats': stats,
        'upcoming': upcoming,
        'overdue': overdue,
        'recent_completed': recent_completed,
        'monthly_stats': monthly_stats,
        'active_types': active_types,
        'documents': documents,  # <-- ΠΡΟΣΤΕΘΗΚΕ
    }
    
    return render(request, 'accounting/client_detail.html', context)

# ============================================
# OBLIGATION VIEWS - Extracted to views/obligations.py
# ============================================
# Obligation views have been moved to accounting/views/obligations.py
# They are imported at the top of this file from .views.obligations

# ============================================
# EXPORT TO EXCEL
# ============================================

@staff_member_required
def export_filtered_excel(request):
    """
    Export filtered obligations to Excel with formatting
    """
    try:
        # Get filters from request
        filters = _get_filters_from_request(request)
        
        # Build query
        query = _build_export_query(filters)
        
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Υποχρεώσεις"
        
        # Apply styling
        _apply_excel_styling(ws)
        
        # Add headers and data
        _write_excel_headers(ws)
        _write_excel_data(ws, query)
        
        # Auto-adjust columns
        _auto_adjust_excel_columns(ws)
        
        # Prepare response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'Ypohrewseis_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        wb.save(response)
        logger.info(f"Excel exported by {request.user.username}: {query.count()} records")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting Excel: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


# ============================================
# VOIP VIEWS - Extracted to views/voip.py
# ============================================
# VoIP views have been moved to accounting/views/voip.py
# They are imported at the top of this file from .views.voip


# ============================================
# EMAIL VIEWS - Extracted to views/email_views.py
# ============================================
# Email views have been moved to accounting/views/email_views.py
# They are imported at the top of this file from .views.email_views


# ============================================
# NOTIFICATION SYSTEM
# ============================================

@staff_member_required
def get_notifications(request):
    """
    Get user notifications for dashboard
    """
    now = timezone.now()
    notifications = []
    
    # Overdue obligations
    overdue = MonthlyObligation.objects.filter(
        deadline__lt=now.date(),
        status__in=['pending', 'overdue']
    ).select_related('client', 'obligation_type').order_by('deadline')[:10]
    
    for obl in overdue:
        days_overdue = (now.date() - obl.deadline).days
        notifications.append({
            'id': obl.id,
            'type': 'overdue',
            'priority': 'high',
            'title': f'Καθυστερημένη: {obl.obligation_type.name}',
            'message': f'{obl.client.eponimia} - {days_overdue} μέρες καθυστέρηση',
            'deadline': obl.deadline.isoformat(),
            'client_id': obl.client.id,
            'icon': '🔴',
        })
    
    # Due today
    today_obligations = MonthlyObligation.objects.filter(
        deadline=now.date(),
        status='pending'
    ).select_related('client', 'obligation_type')
    
    for obl in today_obligations:
        notifications.append({
            'id': obl.id,
            'type': 'due_today',
            'priority': 'medium',
            'title': f'Λήγει Σήμερα: {obl.obligation_type.name}',
            'message': f'{obl.client.eponimia}',
            'deadline': obl.deadline.isoformat(),
            'client_id': obl.client.id,
            'icon': '⚠️',
        })
    
    # Upcoming (next 3 days)
    next_3_days = now.date() + timedelta(days=3)
    upcoming = MonthlyObligation.objects.filter(
        deadline__range=[now.date() + timedelta(days=1), next_3_days],
        status='pending'
    ).select_related('client', 'obligation_type').order_by('deadline')[:5]
    
    for obl in upcoming:
        days_until = (obl.deadline - now.date()).days
        notifications.append({
            'id': obl.id,
            'type': 'upcoming',
            'priority': 'low',
            'title': f'Προσεχώς: {obl.obligation_type.name}',
            'message': f'{obl.client.eponimia} - σε {days_until} μέρες',
            'deadline': obl.deadline.isoformat(),
            'client_id': obl.client.id,
            'icon': '📅',
        })
    
    return JsonResponse({
        'notifications': notifications,
        'count': len(notifications),
        'overdue_count': len([n for n in notifications if n['type'] == 'overdue']),
        'today_count': len([n for n in notifications if n['type'] == 'due_today']),
    })


# ============================================
# END OF VIEWS
# ============================================

logger.info("Accounting views module loaded successfully")

# ============================================
# TICKET MANAGEMENT VIEWS (NEW!)
# ============================================

@staff_member_required
@require_POST
def assign_ticket(request, ticket_id):
    """Assign ticket to current user"""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        
        # Mark as assigned
        ticket.mark_as_assigned(request.user)
        
        # Log
        VoIPCallLog.objects.create(
            call=ticket.call,
            action='ticket_assigned',
            description=f"Ticket #{ticket_id} assigned to {request.user.username}"
        )
        
        logger.info(f"Ticket #{ticket_id} assigned to {request.user.username}")
        
        return JsonResponse({
            'success': True, 
            'message': f'✅ Ticket ανατέθηκε σε {request.user.get_full_name() or request.user.username}'
        })
        
    except Ticket.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '❌ Ticket δεν βρέθηκε'
        }, status=404)
    except Exception as e:
        logger.error(f"Error assigning ticket: {e}")
        return JsonResponse({
            'success': False,
            'message': f'❌ Σφάλμα: {str(e)}'
        }, status=500)


@staff_member_required
@require_POST
def update_ticket_status(request, ticket_id):
    """Update ticket status and notes"""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON'
            }, status=400)
        
        # Update status
        if 'status' in data and data['status'] in ['open', 'assigned', 'in_progress', 'resolved', 'closed']:
            ticket.status = data['status']
        
        # Update notes
        if 'notes' in data:
            new_note = data['notes']
            timestamp = timezone.now().strftime('%d/%m/%Y %H:%M')
            if ticket.notes:
                ticket.notes += f"\n[{timestamp}] {new_note}"
            else:
                ticket.notes = f"[{timestamp}] {new_note}"
        
        # Auto-mark dates
        if ticket.status == 'resolved' and not ticket.resolved_at:
            ticket.mark_as_resolved()
        elif ticket.status == 'closed' and not ticket.closed_at:
            ticket.mark_as_closed()
        
        ticket.save()
        
        # Log
        VoIPCallLog.objects.create(
            call=ticket.call,
            action='ticket_updated',
            description=f"Ticket #{ticket_id} status → {ticket.get_status_display()}"
        )
        
        logger.info(f"Ticket #{ticket_id} updated to status {ticket.status}")
        
        return JsonResponse({
            'success': True,
            'message': f'✅ Ticket ενημερώθηκε!',
            'ticket': {
                'id': ticket.id,
                'status': ticket.get_status_display(),
                'notes': ticket.notes,
            }
        })
        
    except Ticket.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '❌ Ticket δεν βρέθηκε'
        }, status=404)
    except Exception as e:
        logger.error(f"Error updating ticket: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'❌ Σφάλμα: {str(e)}'
        }, status=500)


# ============================================
# CALENDAR VIEWS - Extracted to views/calendar.py
# ============================================
# Calendar views have been moved to accounting/views/calendar.py
# They are imported at the top of this file from .views.calendar


class ClientDocumentViewSet(viewsets.ModelViewSet):
    queryset = ClientDocument.objects.all()
    serializer_class = ClientDocumentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

# accounting/views.py - Door control using Tasmota
# SECURITY: IP addresses loaded from Django settings

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

# SECURITY FIX: Load IP from settings instead of hardcoding
TASMOTA_IP = settings.TASMOTA_IP
TASMOTA_PORT = settings.TASMOTA_PORT
TIMEOUT = 2  # 2 seconds


@login_required
@require_http_methods(["GET"])
def door_status(request):
    """Check door status - ON or OFF"""
    try:
        url = f"http://{TASMOTA_IP}:{TASMOTA_PORT}/cm?cmnd=Power"
        
        logger.info(f"🔍 Checking status at {TASMOTA_IP}")
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            power = data.get("POWER", "OFF")
            
            logger.info(f"✅ Status: {power}")
            
            return JsonResponse({
                "success": True,
                "status": "open" if power == "ON" else "closed",
                "raw_power": power
            })
        else:
            logger.error(f"❌ HTTP {response.status_code}")
            return JsonResponse({
                "success": False,
                "error": f"HTTP {response.status_code}"
            }, status=500)
            
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout connecting to {TASMOTA_IP}")
        return JsonResponse({
            "success": False,
            "error": "Timeout"
        }, status=504)
        
    except requests.exceptions.ConnectionError:
        logger.error(f"🔴 Cannot connect to {TASMOTA_IP}")
        return JsonResponse({
            "success": False,
            "error": f"Cannot connect to {TASMOTA_IP}"
        }, status=503)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def open_door(request):
    """
    Toggle door - ON ↔ OFF
    ✅ SECURITY FIX: Authentication and CSRF protection enabled to prevent unauthorized door control
    """
    try:
        # TOGGLE command
        url = f"http://{TASMOTA_IP}:{TASMOTA_PORT}/cm?cmnd=Power%20TOGGLE"
        
        logger.info(f"🔄 Toggling door at {TASMOTA_IP}")
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            new_state = data.get("POWER", "UNKNOWN")
            
            logger.info(f"✅ New state: {new_state}")
            
            return JsonResponse({
                "success": True,
                "new_state": new_state,
                "message": f"Πόρτα τώρα: {new_state}"
            })
        else:
            logger.error(f"❌ HTTP {response.status_code}")
            return JsonResponse({
                "success": False,
                "error": f"HTTP {response.status_code}"
            }, status=500)
        
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout toggling door at {TASMOTA_IP}")
        return JsonResponse({
            "success": False,
            "error": "Timeout"
        }, status=504)
        
    except requests.exceptions.ConnectionError:
        logger.error(f"🔴 Cannot connect to {TASMOTA_IP}")
        return JsonResponse({
            "success": False,
            "error": f"Cannot connect to {TASMOTA_IP}"
        }, status=503)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def door_control(request):
    """Unified door control endpoint - requires authentication"""
    if request.method == "POST":
        return open_door(request)
    else:
        return door_status(request)

# ============================================
# GLOBAL SEARCH API
# ============================================

@require_GET
@staff_member_required
def global_search_api(request):
    """
    Global search API for clients and obligations.
    Searches by client name (eponimia), AFM, email, and obligation type.
    Returns max 5 results per category.
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': [], 'clients': [], 'obligations': []})

    try:
        # Search clients by eponimia, afm, email, or phone
        clients = ClientProfile.objects.filter(
            Q(eponimia__icontains=query) |
            Q(afm__icontains=query) |
            Q(email__icontains=query) |
            Q(kinito_tilefono__icontains=query) |
            Q(tilefono_epixeirisis_1__icontains=query)
        ).filter(is_active=True)[:5]

        # Search obligations by client name or obligation type name
        obligations = MonthlyObligation.objects.filter(
            Q(client__eponimia__icontains=query) |
            Q(obligation_type__name__icontains=query) |
            Q(client__afm__icontains=query)
        ).select_related('client', 'obligation_type').order_by('-deadline')[:5]

        # Format results
        clients_data = [{
            'id': c.id,
            'name': c.eponimia,
            'afm': c.afm,
            'email': c.email or '',
            'url': f'/admin/accounting/clientprofile/{c.id}/change/',
            'type': 'client'
        } for c in clients]

        obligations_data = [{
            'id': o.id,
            'name': str(o),
            'client': o.client.eponimia,
            'client_afm': o.client.afm,
            'obligation_type': o.obligation_type.name,
            'period': f'{o.month:02d}/{o.year}',
            'status': o.status,
            'url': f'/admin/accounting/monthlyobligation/{o.id}/change/',
            'type': 'obligation'
        } for o in obligations]

        return JsonResponse({
            'success': True,
            'query': query,
            'clients': clients_data,
            'obligations': obligations_data,
            'total': len(clients_data) + len(obligations_data)
        })

    except Exception as e:
        logger.error(f"Error in global_search_api: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e),
            'clients': [],
            'obligations': []
        }, status=500)


# ============================================
# PDF REPORT GENERATION
# ============================================

@staff_member_required
def client_report_pdf(request, client_id):
    """
    Generate PDF report for a specific client.
    Includes client info and obligation history.
    """
    from io import BytesIO
    from django.template.loader import render_to_string
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(
            'xhtml2pdf δεν είναι εγκατεστημένο. Εγκαταστήστε το με: pip install xhtml2pdf',
            status=500
        )

    client = get_object_or_404(ClientProfile, id=client_id)

    # Get all obligations for stats calculation (before slicing)
    all_obligations = MonthlyObligation.objects.filter(client=client)

    # Calculate statistics from unsliced queryset
    stats = {
        'total': all_obligations.count(),
        'completed': all_obligations.filter(status='completed').count(),
        'pending': all_obligations.filter(status='pending').count(),
        'overdue': all_obligations.filter(status='overdue').count(),
    }

    # Get limited obligations for the table (after stats calculation)
    obligations = all_obligations.select_related('obligation_type').order_by('-deadline')[:50]

    # Completion rate
    if stats['total'] > 0:
        stats['completion_rate'] = round((stats['completed'] / stats['total']) * 100, 1)
    else:
        stats['completion_rate'] = 0

    html_content = render_to_string('reports/client_report.html', {
        'client': client,
        'obligations': obligations,
        'stats': stats,
        'generated_at': timezone.now()
    })

    try:
        result = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=result)
        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)
        pdf = result.getvalue()
        response = HttpResponse(pdf, content_type='application/pdf')
        safe_name = client.afm.replace(' ', '_')
        response['Content-Disposition'] = f'filename="client_{safe_name}.pdf"'
        logger.info(f"PDF report generated for client {client.afm} by {request.user.username}")
        return response
    except Exception as e:
        logger.error(f"Error generating PDF for client {client_id}: {e}", exc_info=True)
        return HttpResponse(f'Σφάλμα δημιουργίας PDF: {str(e)}', status=500)


@staff_member_required
def monthly_report_pdf(request, year, month):
    """
    Generate PDF report for a specific month.
    Includes all obligations for that period.
    """
    from io import BytesIO
    from django.template.loader import render_to_string
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(
            'xhtml2pdf δεν είναι εγκατεστημένο. Εγκαταστήστε το με: pip install xhtml2pdf',
            status=500
        )

    # Get all obligations for stats calculation (before any slicing)
    all_obligations = MonthlyObligation.objects.filter(
        year=year,
        month=month
    )

    # Calculate statistics from base queryset
    stats = {
        'total': all_obligations.count(),
        'completed': all_obligations.filter(status='completed').count(),
        'pending': all_obligations.filter(status='pending').count(),
        'overdue': all_obligations.filter(status='overdue').count(),
    }

    # Completion rate
    if stats['total'] > 0:
        stats['completion_rate'] = round((stats['completed'] / stats['total']) * 100, 1)
    else:
        stats['completion_rate'] = 0

    # Group by status (from base queryset)
    by_status = {
        'pending': all_obligations.filter(status='pending').select_related('client', 'obligation_type'),
        'completed': all_obligations.filter(status='completed').select_related('client', 'obligation_type'),
        'overdue': all_obligations.filter(status='overdue').select_related('client', 'obligation_type'),
    }

    # Get obligations for the table
    obligations = all_obligations.select_related('client', 'obligation_type').order_by('deadline', 'client__eponimia')

    # Month names in Greek
    month_names = {
        1: 'Ιανουάριος', 2: 'Φεβρουάριος', 3: 'Μάρτιος',
        4: 'Απρίλιος', 5: 'Μάιος', 6: 'Ιούνιος',
        7: 'Ιούλιος', 8: 'Αύγουστος', 9: 'Σεπτέμβριος',
        10: 'Οκτώβριος', 11: 'Νοέμβριος', 12: 'Δεκέμβριος'
    }
    month_name = month_names.get(month, str(month))

    html_content = render_to_string('reports/monthly_report.html', {
        'year': year,
        'month': month,
        'month_name': month_name,
        'obligations': obligations,
        'stats': stats,
        'by_status': by_status,
        'generated_at': timezone.now()
    })

    try:
        result = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=result)
        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)
        pdf = result.getvalue()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="report_{year}_{month:02d}.pdf"'
        logger.info(f"Monthly PDF report generated for {month}/{year} by {request.user.username}")
        return response
    except Exception as e:
        logger.error(f"Error generating monthly PDF for {month}/{year}: {e}", exc_info=True)
        return HttpResponse(f'Σφάλμα δημιουργίας PDF: {str(e)}', status=500)
