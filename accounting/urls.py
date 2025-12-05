"""
Accounting URLs Configuration
Author: ddiplas
Version: 2.3
Description: Unified and optimized URL routing for the Accounting app.
             Includes JWT auth endpoints and API documentation.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_auth
from .api_clients import ClientViewSet
from .api_obligations import ObligationViewSet, ObligationTypeViewSet
from .api_dashboard import (
    dashboard_stats,
    dashboard_calendar,
    dashboard_recent_activity,
    dashboard_client_stats
)
from .api_obligation_profiles import (
    client_obligation_profile,
    obligation_types_grouped,
    obligation_profiles_list,
    generate_month_obligations
)
from .api_obligation_settings import (
    ObligationTypeSettingsViewSet,
    ObligationProfileSettingsViewSet,
    ObligationGroupSettingsViewSet,
)
from .api_voip import (
    VoIPCallViewSet as VoIPCallViewSetV2,
    TicketViewSet,
    calls_stats,
    tickets_stats,
    search_clients_for_match,
)


app_name = "accounting"

# ============================================
# REST API ROUTER SETUP
# ============================================
router = DefaultRouter()
router.register(r"voip-calls", views.VoIPCallViewSet, basename="voip-call")
router.register(r"voip-call-logs", views.VoIPCallLogViewSet, basename="voip-call-log")

# New enhanced VoIP/Tickets router (v2)
router_v2 = DefaultRouter()
router_v2.register(r'calls', VoIPCallViewSetV2, basename='calls')
router_v2.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'documents', views.ClientDocumentViewSet)
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'obligations', ObligationViewSet, basename='obligation')
router.register(r'obligation-types', ObligationTypeViewSet, basename='obligation-type')

# Settings management ViewSets
router.register(r'settings/obligation-types', ObligationTypeSettingsViewSet, basename='settings-obligation-type')
router.register(r'settings/obligation-profiles', ObligationProfileSettingsViewSet, basename='settings-obligation-profile')
router.register(r'settings/obligation-groups', ObligationGroupSettingsViewSet, basename='settings-obligation-group')
# ============================================
# URL PATTERNS
# ============================================
urlpatterns = [
    # MAIN VIEWS
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("reports/", views.reports_view, name="reports"),
    path("client/<int:client_id>/", views.client_detail_view, name="client_detail"),

    # CALENDAR
    path("calendar/", views.calendar_view, name="calendar"),
    path("api/calendar-events/", views.calendar_events_api, name="calendar_events_api"),

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
    path("bulk-complete/", views.bulk_complete_obligations, name="bulk_complete"),  # Enhanced bulk complete with email & file
    path("advanced-bulk-complete/", views.advanced_bulk_complete, name="advanced_bulk_complete"),

    # EXPORT
    path("export-excel/", views.export_filtered_excel, name="export_excel"),

    # VOIP MANAGEMENT
    path("voip/dashboard/", views.voip_dashboard, name="voip_dashboard"),
    path("voip/list/", views.VoIPCallsListView.as_view(), name="voip_list"),

    # Fritz!Box Webhook (Token authenticated, no session required)
    path("api/fritz-webhook/", views.fritz_webhook, name="fritz_webhook"),

    # AJAX / API Endpoints
    path("voip/api/calls/", views.voip_calls_api, name="voip_calls_api"),
    path("voip/api/update/<int:call_id>/", views.voip_call_update, name="voip_call_update"),
    path("voip/api/statistics/", views.voip_statistics, name="voip_statistics"),
    path("voip/api/bulk-action/", views.voip_bulk_action, name="voip_bulk_action"),

    # Export
    path("voip/export/csv/", views.voip_export_csv, name="voip_export_csv"),

    # EMAIL AUTOMATION API
    path("api/email-templates/", views.api_email_templates, name="api_email_templates"),
    path("api/email-template/<int:template_id>/", views.api_email_template_detail, name="api_email_template_detail"),
    path("api/send-bulk-email/", views.api_send_bulk_email, name="api_send_bulk_email"),
    path("api/send-bulk-email-direct/", views.api_send_bulk_email_direct, name="api_send_bulk_email_direct"),

    # OBLIGATION API
    path("api/obligation-check/", views.check_obligation_duplicate, name="check_obligation"),

    # WIZARD API
    path("api/obligations-wizard/", views.api_obligations_wizard, name="api_obligations_wizard"),
    path("wizard-bulk-process/", views.wizard_bulk_process, name="wizard_bulk_process"),

    # GLOBAL SEARCH API
    path("api/search/", views.global_search_api, name="global_search_api"),

    # PDF REPORTS
    path("reports/client/<int:client_id>/pdf/", views.client_report_pdf, name="client_report_pdf"),
    path("reports/monthly/<int:year>/<int:month>/pdf/", views.monthly_report_pdf, name="monthly_report_pdf"),

    # TICKET MANAGEMENT
    path("ticket/<int:ticket_id>/assign/", views.assign_ticket, name="assign_ticket"),
    path("ticket/<int:ticket_id>/update/", views.update_ticket_status, name="update_ticket_status"),
    path("ticket/send-email/", views.send_ticket_email, name="send_ticket_email"),

    # DASHBOARD API
    path("api/dashboard/stats/", dashboard_stats, name="api_dashboard_stats"),
    path("api/dashboard/calendar/", dashboard_calendar, name="api_dashboard_calendar"),
    path("api/dashboard/recent-activity/", dashboard_recent_activity, name="api_dashboard_recent_activity"),
    path("api/dashboard/client-stats/", dashboard_client_stats, name="api_dashboard_client_stats"),

    # ============================================
    # OBLIGATION PROFILE APIs
    # ============================================
    path("api/v1/clients/<int:client_id>/obligation-profile/", client_obligation_profile, name="client_obligation_profile"),
    path("api/v1/obligation-types/grouped/", obligation_types_grouped, name="obligation_types_grouped"),
    path("api/v1/obligation-profiles/", obligation_profiles_list, name="obligation_profiles_list"),
    path("api/v1/obligations/generate-month/", generate_month_obligations, name="generate_month_obligations"),

    # REST ROUTER
    path("api/", include(router.urls)),
    path("api/v1/", include(router.urls)),  # Versioned API endpoint

    # ============================================
    # ENHANCED VOIP/TICKETS API (v2)
    # ============================================
    path("api/v1/", include(router_v2.urls)),  # New calls/tickets endpoints
    path("api/v1/calls/stats/", calls_stats, name="api_calls_stats"),
    path("api/v1/tickets/stats/", tickets_stats, name="api_tickets_stats"),
    path("api/v1/clients/search-for-match/", search_clients_for_match, name="search_clients_for_match"),

    # ==================================================
    # JWT AUTHENTICATION ENDPOINTS
    # ==================================================
    path("api/auth/login/", api_auth.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", api_auth.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", api_auth.logout_view, name="auth_logout"),
    path("api/auth/me/", api_auth.current_user_view, name="auth_me"),

    # ==================================================
    # UTILITY ENDPOINTS
    # ==================================================
    path("api/health/", api_auth.health_check, name="api_health"),
    path("api/test/", api_auth.api_test, name="api_test"),
]
