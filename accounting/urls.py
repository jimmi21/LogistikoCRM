"""
Accounting URLs Configuration
Author: ddiplas
Version: 2.2
Description: Unified and optimized URL routing for the Accounting app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = "accounting"

# ============================================
# REST API ROUTER SETUP
# ============================================
router = DefaultRouter()
router.register(r"voip-calls", views.VoIPCallViewSet, basename="voip-call")
router.register(r"voip-call-logs", views.VoIPCallLogViewSet, basename="voip-call-log")
router.register(r'documents', views.ClientDocumentViewSet)
# ============================================
# URL PATTERNS
# ============================================
urlpatterns = [
    # MAIN VIEWS
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("reports/", views.reports_view, name="reports"),
    path("client/<int:client_id>/", views.client_detail_view, name="client_detail"),

    # CALENDAR (προαιρετικά)
    path("calendar/", views.calendar_view, name="calendar"),

    path('door-status/', views.door_status, name='door_status'),
    path('open-door/', views.open_door, name='open_door'),
    path('door-control/', views.door_control, name='door_control'),   
    
    # NOTIFICATIONS

    path("notifications/", views.get_notifications, name="notifications"),
    path("api/notifications/", views.get_notifications, name="api_notifications"),

    # OBLIGATION ACTIONS
    path("obligation/<int:obligation_id>/", views.obligation_detail_view, name="obligation_detail"),
    path("obligation/<int:obligation_id>/complete/", views.quick_complete_obligation, name="obligation_complete"),
    path("obligation/<int:obligation_id>/complete-with-file/", views.complete_with_file, name="obligation_complete_file"),
    path("quick-complete/<int:obligation_id>/", views.quick_complete_obligation, name="quick_complete"),  # Legacy
    path("bulk-complete/", views.bulk_complete_view, name="bulk_complete"),
    path("advanced-bulk-complete/", views.advanced_bulk_complete, name="advanced_bulk_complete"),

    # EXPORT
    path("export-excel/", views.export_filtered_excel, name="export_excel"),

    # VOIP MANAGEMENT
    path("voip/dashboard/", views.voip_dashboard, name="voip_dashboard"),
    path("voip/list/", views.VoIPCallsListView.as_view(), name="voip_list"),

    # AJAX / API Endpoints
    path("voip/api/calls/", views.voip_calls_api, name="voip_calls_api"),
    path("voip/api/update/<int:call_id>/", views.voip_call_update, name="voip_call_update"),
    path("voip/api/statistics/", views.voip_statistics, name="voip_statistics"),
    path("voip/api/bulk-action/", views.voip_bulk_action, name="voip_bulk_action"),

    # Export
    path("voip/export/csv/", views.voip_export_csv, name="voip_export_csv"),

    # EMAIL AUTOMATION API
    path("api/email-templates/", views.api_email_templates, name="api_email_templates"),
    path("api/send-bulk-email/", views.api_send_bulk_email, name="api_send_bulk_email"),

    # OBLIGATION API
    path("api/obligation-check/", views.check_obligation_duplicate, name="check_obligation"),

    # TICKET MANAGEMENT
    path("ticket/<int:ticket_id>/assign/", views.assign_ticket, name="assign_ticket"),
    path("ticket/<int:ticket_id>/update/", views.update_ticket_status, name="update_ticket_status"),
    path("ticket/send-email/", views.send_ticket_email, name="send_ticket_email"),

    # REST ROUTER
    path("api/", include(router.urls)),
]
