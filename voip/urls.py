# -*- coding: utf-8 -*-
"""
voip/urls.py
URL configuration for VoIP app.

API Endpoints:
- GET  /api/voip/calls/           - List calls with filters
- GET  /api/voip/calls/{id}/      - Single call detail
- GET  /api/voip/calls/stats/     - Call statistics
- GET  /api/voip/tickets/         - List VoIP tickets
- POST /api/voip/tickets/         - Create ticket from missed call
- PATCH /api/voip/tickets/{id}/resolve/ - Mark resolved
- PATCH /api/voip/tickets/{id}/assign/  - Assign ticket
- PATCH /api/voip/tickets/{id}/close/   - Close ticket
- GET  /api/voip/tickets/stats/   - Ticket statistics
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from voip.views.callback import ConnectionView
from voip.views.voipwebhook import VoIPWebHook
from voip.api import CallLogViewSet, VoIPTicketViewSet


# DRF Router for API endpoints
router = DefaultRouter()
router.register(r'calls', CallLogViewSet, basename='voip-calls')
router.register(r'tickets', VoIPTicketViewSet, basename='voip-tickets')


urlpatterns = [
    # Existing webhook/callback endpoints
    path('get-callback/',
         ConnectionView.as_view(),
         name='get_callback'
         ),
    path('zd/',
         VoIPWebHook.as_view(),
         name='voip-zadarma-pbx-notification'
         ),

    # REST API endpoints
    path('api/', include(router.urls)),
]
