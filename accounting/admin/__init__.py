# -*- coding: utf-8 -*-
"""
Accounting Admin Module

This module organizes all Django admin classes for the accounting app.
The admin.py file has been split into smaller, more manageable modules:

- clients.py: ClientProfileAdmin, ClientDocumentAdmin, ArchiveConfigurationAdmin
- obligations.py: ObligationGroupAdmin, ObligationProfileAdmin, ObligationTypeAdmin,
                  ClientObligationAdmin, MonthlyObligationAdmin
- email.py: EmailTemplateAdmin, EmailAutomationRuleAdmin, ScheduledEmailAdmin, EmailLogAdmin
- voip.py: VoIPCallAdmin, VoIPCallLogAdmin, TicketAdmin
- mixins.py: Shared inline classes (VoIPCallInline, ClientProfileDocumentInline, etc.)
"""
from django.contrib import admin

# Import all admin classes to ensure they are registered
# Client-related admins
from .clients import (
    ClientProfileAdmin,
    ClientDocumentAdmin,
    ArchiveConfigurationAdmin,
)

# Obligation-related admins
from .obligations import (
    ObligationGroupAdmin,
    ObligationProfileAdmin,
    ObligationTypeAdmin,
    ClientObligationAdmin,
    MonthlyObligationAdmin,
)

# Email-related admins
from .email import (
    EmailTemplateAdmin,
    EmailAutomationRuleAdmin,
    ScheduledEmailAdmin,
    EmailLogAdmin,
)

# VoIP and Ticket admins
from .voip import (
    VoIPCallAdmin,
    VoIPCallLogAdmin,
    TicketAdmin,
)

# Mixins (inline classes) - exported for potential reuse
from .mixins import (
    VoIPCallInline,
    ClientProfileDocumentInline,
    ClientDocumentInline,
    EmailLogInline,
)

# ============================================================================
# CUSTOM ADMIN SITE CONFIGURATION
# ============================================================================

admin.site.index_template = 'admin/custom_index.html'
admin.site.site_header = 'D.P. Economy Administration'
admin.site.site_title = 'D.P. Economy'
admin.site.index_title = 'Καλώς ήρθατε στο D.P. Economy'


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Client admins
    'ClientProfileAdmin',
    'ClientDocumentAdmin',
    'ArchiveConfigurationAdmin',
    # Obligation admins
    'ObligationGroupAdmin',
    'ObligationProfileAdmin',
    'ObligationTypeAdmin',
    'ClientObligationAdmin',
    'MonthlyObligationAdmin',
    # Email admins
    'EmailTemplateAdmin',
    'EmailAutomationRuleAdmin',
    'ScheduledEmailAdmin',
    'EmailLogAdmin',
    # VoIP admins
    'VoIPCallAdmin',
    'VoIPCallLogAdmin',
    'TicketAdmin',
    # Mixins/Inlines
    'VoIPCallInline',
    'ClientProfileDocumentInline',
    'ClientDocumentInline',
    'EmailLogInline',
]
