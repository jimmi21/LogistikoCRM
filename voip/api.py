# -*- coding: utf-8 -*-
"""
voip/api.py
VoIP REST API Views for React frontend integration.

Endpoints:
- GET /api/voip/calls/ - List calls with filters
- GET /api/voip/calls/{id}/ - Single call detail
- GET /api/voip/calls/stats/ - Call statistics
- GET /api/voip/tickets/ - List VoIP tickets
- POST /api/voip/tickets/ - Create ticket from missed call
- PATCH /api/voip/tickets/{id}/resolve/ - Mark ticket resolved
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from django.db.models import Avg, Count, Q
from django.db.models.functions import ExtractHour, TruncDate
from django.utils import timezone
from datetime import timedelta

from accounting.models import VoIPCall, Ticket
from .serializers import (
    CallLogSerializer,
    CallLogDetailSerializer,
    CallStatsSerializer,
    VoIPTicketSerializer,
    VoIPTicketCreateSerializer,
)


class CallLogFilter(FilterSet):
    """
    Filters for VoIP call logs.
    """
    direction = filters.ChoiceFilter(choices=VoIPCall.DIRECTION_CHOICES)
    answered = filters.BooleanFilter(method='filter_answered')
    date_from = filters.DateFilter(field_name='started_at', lookup_expr='date__gte')
    date_to = filters.DateFilter(field_name='started_at', lookup_expr='date__lte')
    status = filters.ChoiceFilter(choices=VoIPCall.STATUS_CHOICES)
    client = filters.NumberFilter(field_name='client__id')
    has_ticket = filters.BooleanFilter(field_name='ticket_created')

    class Meta:
        model = VoIPCall
        fields = ['direction', 'status', 'client', 'ticket_created']

    def filter_answered(self, queryset, name, value):
        """Filter by answered/missed status."""
        if value is True:
            return queryset.exclude(status='missed')
        elif value is False:
            return queryset.filter(status='missed')
        return queryset


class CallLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for VoIP call logs.

    list:
    Return a list of all calls with optional filters.

    retrieve:
    Return detailed information about a specific call.

    stats:
    Return call statistics for dashboard.
    """
    queryset = VoIPCall.objects.select_related('client').order_by('-started_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CallLogFilter
    search_fields = ['phone_number', 'client__eponimia', 'client__afm']
    ordering_fields = ['started_at', 'duration_seconds', 'status']
    ordering = ['-started_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CallLogDetailSerializer
        return CallLogSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get call statistics for dashboard.

        Returns:
        - total_calls_today: Total calls today
        - missed_calls_today: Missed calls today
        - answered_calls_today: Answered calls today
        - avg_duration: Average call duration in seconds
        - avg_duration_formatted: Formatted average duration
        - calls_by_hour: List of call counts by hour (for chart)
        - calls_by_direction: Breakdown by direction
        - total_calls_week: Total calls this week
        - missed_calls_week: Missed calls this week
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        today_start = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time())
        )
        week_start = timezone.make_aware(
            timezone.datetime.combine(week_ago, timezone.datetime.min.time())
        )

        # Today's stats
        today_calls = VoIPCall.objects.filter(started_at__gte=today_start)
        total_today = today_calls.count()
        missed_today = today_calls.filter(status='missed').count()
        answered_today = total_today - missed_today

        # Average duration (only completed calls)
        avg_duration_result = VoIPCall.objects.filter(
            status='completed'
        ).aggregate(avg_duration=Avg('duration_seconds'))
        avg_duration = avg_duration_result['avg_duration'] or 0

        # Format average duration
        avg_minutes = int(avg_duration // 60)
        avg_seconds = int(avg_duration % 60)
        avg_duration_formatted = f"{avg_minutes:02d}:{avg_seconds:02d}"

        # Calls by hour (for chart) - last 24 hours
        calls_by_hour = []
        for hour in range(24):
            hour_start = today_start.replace(hour=hour)
            hour_end = hour_start + timedelta(hours=1)
            count = VoIPCall.objects.filter(
                started_at__gte=hour_start,
                started_at__lt=hour_end
            ).count()
            calls_by_hour.append({
                'hour': hour,
                'hour_display': f"{hour:02d}:00",
                'count': count
            })

        # Calls by direction
        direction_stats = VoIPCall.objects.filter(
            started_at__gte=today_start
        ).values('direction').annotate(count=Count('id'))

        calls_by_direction = {
            'incoming': 0,
            'outgoing': 0
        }
        for stat in direction_stats:
            calls_by_direction[stat['direction']] = stat['count']

        # Week stats
        week_calls = VoIPCall.objects.filter(started_at__gte=week_start)
        total_week = week_calls.count()
        missed_week = week_calls.filter(status='missed').count()

        stats_data = {
            'total_calls_today': total_today,
            'missed_calls_today': missed_today,
            'answered_calls_today': answered_today,
            'avg_duration': round(avg_duration, 2),
            'avg_duration_formatted': avg_duration_formatted,
            'calls_by_hour': calls_by_hour,
            'calls_by_direction': calls_by_direction,
            'total_calls_week': total_week,
            'missed_calls_week': missed_week,
        }

        serializer = CallStatsSerializer(data=stats_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class VoIPTicketFilter(FilterSet):
    """
    Filters for VoIP tickets.
    """
    status = filters.ChoiceFilter(choices=Ticket.STATUS_CHOICES)
    priority = filters.ChoiceFilter(choices=Ticket.PRIORITY_CHOICES)
    assigned_to = filters.NumberFilter()
    client = filters.NumberFilter()
    is_open = filters.BooleanFilter(method='filter_is_open')
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to', 'client']

    def filter_is_open(self, queryset, name, value):
        """Filter by open/closed status."""
        open_statuses = ['open', 'assigned', 'in_progress']
        if value is True:
            return queryset.filter(status__in=open_statuses)
        elif value is False:
            return queryset.exclude(status__in=open_statuses)
        return queryset


class VoIPTicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint for VoIP tickets.

    list:
    Return a list of all VoIP tickets.

    create:
    Create a new ticket from a missed call.

    retrieve:
    Return detailed information about a specific ticket.

    resolve:
    Mark a ticket as resolved.
    """
    queryset = Ticket.objects.select_related(
        'call', 'client', 'assigned_to'
    ).order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VoIPTicketFilter
    search_fields = ['title', 'description', 'client__eponimia', 'call__phone_number']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return VoIPTicketCreateSerializer
        return VoIPTicketSerializer

    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """
        Mark ticket as resolved.

        Optional body:
        - notes: Additional resolution notes
        """
        ticket = self.get_object()

        if ticket.status in ['resolved', 'closed']:
            return Response(
                {'error': 'Το ticket είναι ήδη επιλυμένο.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update notes if provided
        notes = request.data.get('notes')
        if notes:
            ticket.notes = f"{ticket.notes}\n\n--- Επίλυση ---\n{notes}".strip()

        ticket.mark_as_resolved()

        serializer = VoIPTicketSerializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Assign ticket to a user.

        Required body:
        - assigned_to: User ID
        """
        ticket = self.get_object()
        user_id = request.data.get('assigned_to')

        if not user_id:
            return Response(
                {'error': 'Απαιτείται το πεδίο assigned_to.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Ο χρήστης δεν βρέθηκε.'},
                status=status.HTTP_404_NOT_FOUND
            )

        ticket.mark_as_assigned(user)

        serializer = VoIPTicketSerializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def close(self, request, pk=None):
        """
        Mark ticket as closed.
        """
        ticket = self.get_object()

        if ticket.status == 'closed':
            return Response(
                {'error': 'Το ticket είναι ήδη κλειστό.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket.mark_as_closed()

        serializer = VoIPTicketSerializer(ticket)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get ticket statistics.

        Returns:
        - open_count: Number of open tickets
        - assigned_count: Number of assigned tickets
        - in_progress_count: Number of in-progress tickets
        - resolved_today: Tickets resolved today
        - avg_response_time: Average response time in seconds
        """
        today = timezone.now().date()
        today_start = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time())
        )

        open_count = Ticket.objects.filter(status='open').count()
        assigned_count = Ticket.objects.filter(status='assigned').count()
        in_progress_count = Ticket.objects.filter(status='in_progress').count()
        resolved_today = Ticket.objects.filter(
            resolved_at__gte=today_start
        ).count()

        # Calculate average response time for assigned tickets
        assigned_tickets = Ticket.objects.filter(
            assigned_at__isnull=False
        ).exclude(assigned_at=None)

        total_response_time = 0
        count = 0
        for ticket in assigned_tickets:
            if ticket.response_time_seconds:
                total_response_time += ticket.response_time_seconds
                count += 1

        avg_response_time = total_response_time / count if count > 0 else 0

        return Response({
            'open_count': open_count,
            'assigned_count': assigned_count,
            'in_progress_count': in_progress_count,
            'resolved_today': resolved_today,
            'avg_response_time': round(avg_response_time, 2),
            'avg_response_time_formatted': f"{int(avg_response_time // 60)}:{int(avg_response_time % 60):02d}",
        })
