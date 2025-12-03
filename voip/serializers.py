# -*- coding: utf-8 -*-
"""
voip/serializers.py
VoIP REST API Serializers for React frontend integration.
"""
from rest_framework import serializers
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from accounting.models import VoIPCall, VoIPCallLog, Ticket, ClientProfile


class CallLogSerializer(serializers.ModelSerializer):
    """
    Serializer for VoIP call list view.
    Includes client name and formatted duration.
    """
    client_name = serializers.CharField(source='client.eponimia', read_only=True)
    client_afm = serializers.CharField(source='client.afm', read_only=True)
    duration_formatted = serializers.CharField(read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VoIPCall
        fields = [
            'id',
            'call_id',
            'phone_number',
            'direction',
            'direction_display',
            'status',
            'status_display',
            'started_at',
            'ended_at',
            'duration_seconds',
            'duration_formatted',
            'client',
            'client_name',
            'client_afm',
            'notes',
            'resolution',
            'ticket_created',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'duration_formatted']


class CallLogDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single call view.
    Includes all fields plus related ticket info.
    """
    client_name = serializers.CharField(source='client.eponimia', read_only=True)
    client_afm = serializers.CharField(source='client.afm', read_only=True)
    client_email = serializers.EmailField(source='client.email', read_only=True)
    client_phone = serializers.CharField(source='client.kinito_tilefono', read_only=True)
    duration_formatted = serializers.CharField(read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resolution_display = serializers.CharField(source='get_resolution_display', read_only=True)
    ticket_info = serializers.SerializerMethodField()
    logs = serializers.SerializerMethodField()

    class Meta:
        model = VoIPCall
        fields = [
            'id',
            'call_id',
            'phone_number',
            'direction',
            'direction_display',
            'status',
            'status_display',
            'started_at',
            'ended_at',
            'duration_seconds',
            'duration_formatted',
            'client',
            'client_name',
            'client_afm',
            'client_email',
            'client_phone',
            'notes',
            'resolution',
            'resolution_display',
            'ticket_created',
            'ticket_id',
            'ticket_info',
            'logs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_ticket_info(self, obj):
        """Get associated ticket information if exists."""
        try:
            ticket = obj.ticket
            return {
                'id': ticket.id,
                'title': ticket.title,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at,
            }
        except Ticket.DoesNotExist:
            return None

    def get_logs(self, obj):
        """Get call activity logs."""
        logs = obj.logs.all()[:10]  # Last 10 logs
        return [
            {
                'action': log.action,
                'description': log.description,
                'created_at': log.created_at,
            }
            for log in logs
        ]


class CallStatsSerializer(serializers.Serializer):
    """
    Serializer for call statistics endpoint.
    """
    total_calls_today = serializers.IntegerField()
    missed_calls_today = serializers.IntegerField()
    answered_calls_today = serializers.IntegerField()
    avg_duration = serializers.FloatField()
    avg_duration_formatted = serializers.CharField()
    calls_by_hour = serializers.ListField(
        child=serializers.DictField()
    )
    calls_by_direction = serializers.DictField()
    total_calls_week = serializers.IntegerField()
    missed_calls_week = serializers.IntegerField()


class VoIPTicketSerializer(serializers.ModelSerializer):
    """
    Serializer for VoIP tickets (created from missed calls).
    """
    client_name = serializers.CharField(source='client.eponimia', read_only=True)
    client_afm = serializers.CharField(source='client.afm', read_only=True)
    call_phone = serializers.CharField(source='call.phone_number', read_only=True)
    call_time = serializers.DateTimeField(source='call.started_at', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    days_open = serializers.IntegerField(source='days_since_created', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'call',
            'call_phone',
            'call_time',
            'client',
            'client_name',
            'client_afm',
            'title',
            'description',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'assigned_to',
            'assigned_to_name',
            'notes',
            'days_open',
            'email_sent',
            'follow_up_scheduled',
            'created_at',
            'assigned_at',
            'resolved_at',
            'closed_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'assigned_at', 'resolved_at', 'closed_at'
        ]


class VoIPTicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tickets from missed calls.
    """
    class Meta:
        model = Ticket
        fields = [
            'call',
            'client',
            'title',
            'description',
            'priority',
            'assigned_to',
            'notes',
        ]

    def validate_call(self, value):
        """Ensure call doesn't already have a ticket."""
        if hasattr(value, 'ticket'):
            raise serializers.ValidationError(
                "Αυτή η κλήση έχει ήδη ticket."
            )
        return value

    def create(self, validated_data):
        """Create ticket and update the call."""
        call = validated_data.get('call')

        # Auto-set client from call if not provided
        if not validated_data.get('client') and call.client:
            validated_data['client'] = call.client

        # Auto-generate title if not provided
        if not validated_data.get('title'):
            client_name = call.client.eponimia if call.client else 'Άγνωστος'
            validated_data['title'] = f"Αναπάντητη κλήση από {client_name} ({call.phone_number})"

        ticket = super().create(validated_data)

        # Update call to mark ticket created
        call.ticket_created = True
        call.ticket_id = str(ticket.id)
        call.save(update_fields=['ticket_created', 'ticket_id'])

        # Create log entry
        VoIPCallLog.objects.create(
            call=call,
            action='ticket_created',
            description=f'Ticket #{ticket.id} δημιουργήθηκε'
        )

        return ticket
