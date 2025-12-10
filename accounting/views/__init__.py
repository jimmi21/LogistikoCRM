# accounting/views/__init__.py
"""
Accounting Views Package

This package organizes the accounting views into separate modules for better maintainability.
"""

# Helper functions (internal use)
from .helpers import (
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

# VoIP views
from .voip import (
    # Function-based views
    voip_dashboard,
    fritz_webhook,
    voip_calls_api,
    voip_call_update,
    voip_statistics,
    voip_bulk_action,
    voip_export_csv,
    # Class-based views
    VoIPCallViewSet,
    VoIPCallsListView,
    VoIPCallLogViewSet,
)

__all__ = [
    # Helpers
    '_safe_int',
    '_calculate_dashboard_stats',
    '_build_filtered_query',
    '_calculate_monthly_stats',
    '_process_individual_obligations',
    '_process_grouped_obligations',
    '_match_client_by_phone_standalone',
    '_format_voip_call',
    '_get_status_color',
    '_get_resolution_color',
    '_calculate_success_rate',
    '_log_voip_change',
    '_calculate_send_time',
    '_create_bulk_emails',
    '_get_filters_from_request',
    '_build_export_query',
    '_apply_excel_styling',
    '_write_excel_headers',
    '_write_excel_data',
    '_auto_adjust_excel_columns',
    '_calculate_monthly_completion_stats',
    '_calculate_client_performance',
    '_calculate_time_stats',
    '_calculate_revenue',
    '_calculate_type_stats',
    '_calculate_current_month_stats',
    '_format_chart_data',
    # VoIP function-based views
    'voip_dashboard',
    'fritz_webhook',
    'voip_calls_api',
    'voip_call_update',
    'voip_statistics',
    'voip_bulk_action',
    'voip_export_csv',
    # VoIP class-based views
    'VoIPCallViewSet',
    'VoIPCallsListView',
    'VoIPCallLogViewSet',
]
