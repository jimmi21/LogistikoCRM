# -*- coding: utf-8 -*-
"""
accounting/utils - Utility modules for accounting app
"""

from .report_constants import (
    # Greek months
    GREEK_MONTHS_FULL,
    GREEK_MONTHS_SHORT,
    GREEK_MONTHS_GENITIVE,
    get_greek_month_name,
    # Date ranges
    REPORT_PERIODS,
    get_date_range,
    get_previous_period_range,
    # Excel styling
    BRAND_COLOR,
    BRAND_COLOR_LIGHT,
    STATUS_COLORS,
    get_excel_header_style,
    get_excel_border,
    get_excel_title_style,
    get_status_fill,
    get_alternating_row_fill,
    apply_header_style,
    auto_adjust_column_width,
    # Export formats
    EXPORT_FORMATS,
    get_export_filename,
    get_content_type,
    # Status constants
    OBLIGATION_STATUS_CHOICES,
    OBLIGATION_STATUS_ICONS,
    get_status_display,
    get_status_icon,
    # Type colors
    OBLIGATION_TYPE_COLORS,
    get_type_color,
)

__all__ = [
    # Greek months
    'GREEK_MONTHS_FULL',
    'GREEK_MONTHS_SHORT',
    'GREEK_MONTHS_GENITIVE',
    'get_greek_month_name',
    # Date ranges
    'REPORT_PERIODS',
    'get_date_range',
    'get_previous_period_range',
    # Excel styling
    'BRAND_COLOR',
    'BRAND_COLOR_LIGHT',
    'STATUS_COLORS',
    'get_excel_header_style',
    'get_excel_border',
    'get_excel_title_style',
    'get_status_fill',
    'get_alternating_row_fill',
    'apply_header_style',
    'auto_adjust_column_width',
    # Export formats
    'EXPORT_FORMATS',
    'get_export_filename',
    'get_content_type',
    # Status constants
    'OBLIGATION_STATUS_CHOICES',
    'OBLIGATION_STATUS_ICONS',
    'get_status_display',
    'get_status_icon',
    # Type colors
    'OBLIGATION_TYPE_COLORS',
    'get_type_color',
]
