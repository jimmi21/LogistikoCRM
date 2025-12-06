"""
Accounting Views Module
Re-exports all views from views_main.py for backwards compatibility
"""
# Explicit imports for backwards compatibility with urls.py
from .views_main import (
    # Main views
    dashboard_view,
    client_detail_view,
    reports_view,
    obligation_detail_view,

    # Obligation actions
    quick_complete_obligation,
    complete_with_file,
    bulk_complete_obligations,
    advanced_bulk_complete,

    # Calendar
    calendar_view,
    calendar_events_api,

    # Door control
    door_status,
    open_door,
    door_control,

    # Notifications
    get_notifications,

    # Export
    export_filtered_excel,

    # VoIP
    voip_dashboard,
    fritz_webhook,
    voip_calls_api,
    voip_call_update,
    voip_statistics,
    voip_bulk_action,
    voip_export_csv,
    VoIPCallViewSet,
    VoIPCallLogViewSet,
    VoIPCallsListView,

    # Email API
    api_email_templates,
    api_email_template_detail,
    api_send_bulk_email,
    api_send_bulk_email_direct,

    # Obligation API
    check_obligation_duplicate,
    api_obligations_wizard,
    wizard_bulk_process,

    # Search
    global_search_api,

    # PDF Reports
    client_report_pdf,
    monthly_report_pdf,

    # Tickets
    assign_ticket,
    update_ticket_status,
    send_ticket_email,
)
