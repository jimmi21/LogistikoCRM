# -*- coding: utf-8 -*-
"""
accounting/api_emails.py
Author: Claude
Description: REST API ViewSets for Email Management
             Includes EmailTemplate, ScheduledEmail, EmailAutomationRule, EmailLog
"""

from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, CharFilter,
    NumberFilter, DateFilter, BooleanFilter
)
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from .models import (
    EmailTemplate, EmailLog, EmailAutomationRule, ScheduledEmail,
    MonthlyObligation, ClientProfile, ObligationType
)
from .services.email_service import EmailService


# ============================================
# PAGINATION CLASSES
# ============================================

class EmailPagination(PageNumberPagination):
    """Pagination for email lists"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================
# FILTERS
# ============================================

class EmailLogFilter(FilterSet):
    """Filter for EmailLog"""
    client = NumberFilter(field_name='client_id')
    status = CharFilter(field_name='status')
    date_from = DateFilter(field_name='sent_at__date', lookup_expr='gte')
    date_to = DateFilter(field_name='sent_at__date', lookup_expr='lte')
    search = CharFilter(method='filter_search')

    class Meta:
        model = EmailLog
        fields = ['client', 'status']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(recipient_email__icontains=value) |
                Q(recipient_name__icontains=value) |
                Q(subject__icontains=value) |
                Q(client__eponimia__icontains=value)
            )
        return queryset


class ScheduledEmailFilter(FilterSet):
    """Filter for ScheduledEmail"""
    status = CharFilter(field_name='status')
    date_from = DateFilter(field_name='send_at__date', lookup_expr='gte')
    date_to = DateFilter(field_name='send_at__date', lookup_expr='lte')

    class Meta:
        model = ScheduledEmail
        fields = ['status']


# ============================================
# SERIALIZERS
# ============================================

class ObligationTypeSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for ObligationType in email context"""
    class Meta:
        model = ObligationType
        fields = ['id', 'code', 'name']


class EmailTemplateListSerializer(serializers.ModelSerializer):
    """Serializer for email template list view"""
    obligation_type_name = serializers.CharField(
        source='obligation_type.name', read_only=True, allow_null=True
    )
    obligation_type_code = serializers.CharField(
        source='obligation_type.code', read_only=True, allow_null=True
    )

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'description', 'subject',
            'obligation_type', 'obligation_type_name', 'obligation_type_code',
            'is_active', 'created_at', 'updated_at'
        ]


class EmailTemplateDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for email template"""
    obligation_type_name = serializers.CharField(
        source='obligation_type.name', read_only=True, allow_null=True
    )
    available_variables = serializers.SerializerMethodField()

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'description', 'subject', 'body_html',
            'obligation_type', 'obligation_type_name',
            'is_active', 'created_at', 'updated_at',
            'available_variables'
        ]

    def get_available_variables(self, obj):
        return EmailTemplate.get_available_variables()


class EmailTemplateCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating email templates"""

    class Meta:
        model = EmailTemplate
        fields = [
            'name', 'description', 'subject', 'body_html',
            'obligation_type', 'is_active'
        ]

    def validate_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Το όνομα πρέπει να έχει τουλάχιστον 2 χαρακτήρες."
            )
        return value.strip()

    def validate_subject(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Το θέμα πρέπει να έχει τουλάχιστον 3 χαρακτήρες."
            )
        return value.strip()

    def validate_body_html(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Το κείμενο πρέπει να έχει τουλάχιστον 10 χαρακτήρες."
            )
        return value


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for email log"""
    client_name = serializers.CharField(source='client.eponimia', read_only=True, allow_null=True)
    client_afm = serializers.CharField(source='client.afm', read_only=True, allow_null=True)
    template_name = serializers.CharField(source='template_used.name', read_only=True, allow_null=True)
    sent_by_username = serializers.CharField(source='sent_by.username', read_only=True, allow_null=True)
    status_display = serializers.CharField(read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            'id', 'recipient_email', 'recipient_name',
            'client', 'client_name', 'client_afm',
            'obligation', 'template_used', 'template_name',
            'subject', 'body', 'status', 'status_display',
            'error_message', 'sent_at', 'sent_by', 'sent_by_username'
        ]


class ScheduledEmailListSerializer(serializers.ModelSerializer):
    """Serializer for scheduled email list view"""
    client_name = serializers.CharField(source='client.eponimia', read_only=True, allow_null=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    recipient_count = serializers.IntegerField(read_only=True)
    recipients_display = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledEmail
        fields = [
            'id', 'recipient_email', 'recipient_name', 'recipient_count',
            'recipients_display', 'client', 'client_name',
            'template', 'template_name', 'subject',
            'send_at', 'sent_at', 'status', 'error_message',
            'created_by', 'created_by_username', 'created_at'
        ]

    def get_recipients_display(self, obj):
        return obj.get_recipients_display()


class ScheduledEmailDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for scheduled email"""
    client_name = serializers.CharField(source='client.eponimia', read_only=True, allow_null=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    recipient_count = serializers.IntegerField(read_only=True)
    recipients_list = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledEmail
        fields = [
            'id', 'recipient_email', 'recipient_name', 'recipient_count',
            'recipients_list', 'client', 'client_name',
            'template', 'template_name', 'automation_rule',
            'subject', 'body_html', 'send_at', 'sent_at',
            'status', 'error_message',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]

    def get_recipients_list(self, obj):
        return obj.get_recipients_list()


class ScheduledEmailCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scheduled emails"""
    obligation_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    client_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = ScheduledEmail
        fields = [
            'recipient_email', 'recipient_name', 'client',
            'template', 'subject', 'body_html', 'send_at',
            'obligation_ids', 'client_ids'
        ]

    def validate(self, data):
        if not data.get('recipient_email') and not data.get('client_ids'):
            raise serializers.ValidationError({
                'recipient_email': 'Απαιτείται email παραλήπτη ή επιλογή πελατών.'
            })

        if not data.get('subject'):
            raise serializers.ValidationError({
                'subject': 'Το θέμα είναι υποχρεωτικό.'
            })

        if not data.get('body_html'):
            raise serializers.ValidationError({
                'body_html': 'Το κείμενο είναι υποχρεωτικό.'
            })

        return data

    def create(self, validated_data):
        obligation_ids = validated_data.pop('obligation_ids', [])
        client_ids = validated_data.pop('client_ids', [])

        # Set default send_at if not provided
        if not validated_data.get('send_at'):
            validated_data['send_at'] = timezone.now()

        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user

        scheduled_email = ScheduledEmail.objects.create(**validated_data)

        # Add obligations if provided
        if obligation_ids:
            obligations = MonthlyObligation.objects.filter(id__in=obligation_ids)
            scheduled_email.obligations.set(obligations)

        return scheduled_email


class EmailAutomationRuleListSerializer(serializers.ModelSerializer):
    """Serializer for automation rule list view"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    trigger_display = serializers.CharField(source='get_trigger_display', read_only=True)
    timing_display = serializers.CharField(source='get_timing_display', read_only=True)
    filter_types_count = serializers.SerializerMethodField()

    class Meta:
        model = EmailAutomationRule
        fields = [
            'id', 'name', 'description', 'trigger', 'trigger_display',
            'template', 'template_name', 'timing', 'timing_display',
            'days_before_deadline', 'scheduled_time',
            'is_active', 'filter_types_count',
            'created_at', 'updated_at'
        ]

    def get_filter_types_count(self, obj):
        return obj.filter_obligation_types.count()


class EmailAutomationRuleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for automation rule"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    trigger_display = serializers.CharField(source='get_trigger_display', read_only=True)
    timing_display = serializers.CharField(source='get_timing_display', read_only=True)
    filter_obligation_types_data = ObligationTypeSimpleSerializer(
        source='filter_obligation_types', many=True, read_only=True
    )

    class Meta:
        model = EmailAutomationRule
        fields = [
            'id', 'name', 'description', 'trigger', 'trigger_display',
            'filter_obligation_types', 'filter_obligation_types_data',
            'template', 'template_name', 'timing', 'timing_display',
            'days_before_deadline', 'scheduled_time',
            'is_active', 'created_at', 'updated_at'
        ]


class EmailAutomationRuleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating automation rules"""

    class Meta:
        model = EmailAutomationRule
        fields = [
            'name', 'description', 'trigger', 'filter_obligation_types',
            'template', 'timing', 'days_before_deadline', 'scheduled_time',
            'is_active'
        ]

    def validate_name(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Το όνομα πρέπει να έχει τουλάχιστον 3 χαρακτήρες."
            )
        return value.strip()

    def validate(self, data):
        trigger = data.get('trigger')
        timing = data.get('timing')
        days_before = data.get('days_before_deadline')
        scheduled_time = data.get('scheduled_time')

        if trigger == 'before_deadline' and not days_before:
            raise serializers.ValidationError({
                'days_before_deadline': 'Απαιτείται αριθμός ημερών για trigger "Πριν την προθεσμία".'
            })

        if timing == 'scheduled' and not scheduled_time:
            raise serializers.ValidationError({
                'scheduled_time': 'Απαιτείται ώρα για timing "Συγκεκριμένη ώρα".'
            })

        return data


# ============================================
# SEND EMAIL SERIALIZERS
# ============================================

class SendEmailSerializer(serializers.Serializer):
    """Serializer for sending email directly"""
    to = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1,
        help_text="List of recipient email addresses"
    )
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField()
    template_id = serializers.IntegerField(required=False, allow_null=True)
    client_id = serializers.IntegerField(required=False, allow_null=True)
    obligation_id = serializers.IntegerField(required=False, allow_null=True)


class SendBulkEmailSerializer(serializers.Serializer):
    """Serializer for sending bulk emails"""
    client_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    template_id = serializers.IntegerField()
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    variables = serializers.DictField(required=False, default=dict)


class PreviewEmailSerializer(serializers.Serializer):
    """Serializer for previewing email"""
    template_id = serializers.IntegerField()
    client_id = serializers.IntegerField(required=False, allow_null=True)
    obligation_id = serializers.IntegerField(required=False, allow_null=True)
    variables = serializers.DictField(required=False, default=dict)


# ============================================
# VIEWSETS
# ============================================

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    REST API ViewSet for EmailTemplate

    Endpoints:
    - GET /api/v1/email-templates/ - List all templates
    - POST /api/v1/email-templates/ - Create template
    - GET /api/v1/email-templates/{id}/ - Get single template
    - PUT /api/v1/email-templates/{id}/ - Update template
    - DELETE /api/v1/email-templates/{id}/ - Delete template
    - POST /api/v1/email-templates/{id}/duplicate/ - Duplicate template
    - GET /api/v1/email-templates/variables/ - Get available variables
    """
    queryset = EmailTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailTemplateListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmailTemplateCreateUpdateSerializer
        return EmailTemplateDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by is_active if specified
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset.select_related('obligation_type')

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        POST /api/v1/email-templates/{id}/duplicate/
        Create a copy of an existing template
        """
        original = self.get_object()

        # Create copy with modified name
        copy = EmailTemplate.objects.create(
            name=f"{original.name} (Αντίγραφο)",
            description=original.description,
            subject=original.subject,
            body_html=original.body_html,
            obligation_type=original.obligation_type,
            is_active=False  # New copy starts inactive
        )

        serializer = EmailTemplateDetailSerializer(copy)
        return Response({
            'message': 'Το πρότυπο αντιγράφηκε επιτυχώς.',
            'template': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def variables(self, request):
        """
        GET /api/v1/email-templates/variables/
        Get all available template variables
        """
        variables = EmailTemplate.get_available_variables()
        return Response({
            'variables': [
                {'key': key, 'description': desc}
                for key, desc in variables
            ]
        })

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """
        POST /api/v1/email-templates/{id}/preview/
        Preview rendered template with sample data
        """
        template = self.get_object()
        client_id = request.data.get('client_id')
        obligation_id = request.data.get('obligation_id')

        obligation = None
        client = None

        if obligation_id:
            try:
                obligation = MonthlyObligation.objects.select_related(
                    'client', 'obligation_type'
                ).get(id=obligation_id)
                client = obligation.client
            except MonthlyObligation.DoesNotExist:
                pass
        elif client_id:
            try:
                client = ClientProfile.objects.get(id=client_id)
            except ClientProfile.DoesNotExist:
                pass

        preview = EmailService.preview_email(
            template=template,
            obligation=obligation,
            client=client,
            user=request.user
        )

        return Response(preview)


class ScheduledEmailViewSet(viewsets.ModelViewSet):
    """
    REST API ViewSet for ScheduledEmail

    Endpoints:
    - GET /api/v1/scheduled-emails/ - List (filter: status, date range)
    - POST /api/v1/scheduled-emails/ - Create scheduled email
    - GET /api/v1/scheduled-emails/{id}/ - Get single
    - DELETE /api/v1/scheduled-emails/{id}/ - Cancel (only if pending)
    - POST /api/v1/scheduled-emails/{id}/send-now/ - Send immediately
    """
    queryset = ScheduledEmail.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = EmailPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ScheduledEmailFilter
    ordering_fields = ['send_at', 'created_at', 'status']
    ordering = ['-send_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ScheduledEmailListSerializer
        elif self.action == 'create':
            return ScheduledEmailCreateSerializer
        return ScheduledEmailDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            'client', 'template', 'created_by', 'automation_rule'
        )

    def destroy(self, request, *args, **kwargs):
        """Only allow deletion/cancellation of pending emails"""
        instance = self.get_object()

        if instance.status != 'pending':
            return Response(
                {'error': 'Μόνο τα εκκρεμή email μπορούν να ακυρωθούν.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = 'cancelled'
        instance.save()

        return Response({
            'message': 'Το προγραμματισμένο email ακυρώθηκε.',
            'id': instance.id
        })

    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """
        POST /api/v1/scheduled-emails/{id}/send-now/
        Send a pending scheduled email immediately
        """
        scheduled_email = self.get_object()

        if scheduled_email.status != 'pending':
            return Response(
                {'error': 'Μόνο τα εκκρεμή email μπορούν να σταλούν.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send immediately using EmailService
        from .services.email_service import send_scheduled_email
        success = send_scheduled_email(scheduled_email.id)

        if success:
            scheduled_email.refresh_from_db()
            serializer = ScheduledEmailDetailSerializer(scheduled_email)
            return Response({
                'message': 'Το email στάλθηκε επιτυχώς.',
                'email': serializer.data
            })
        else:
            scheduled_email.refresh_from_db()
            return Response(
                {
                    'error': 'Αποτυχία αποστολής email.',
                    'details': scheduled_email.error_message
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailAutomationRuleViewSet(viewsets.ModelViewSet):
    """
    REST API ViewSet for EmailAutomationRule

    Endpoints:
    - GET /api/v1/email-automations/ - List all rules
    - POST /api/v1/email-automations/ - Create rule
    - GET /api/v1/email-automations/{id}/ - Get single rule
    - PUT /api/v1/email-automations/{id}/ - Update rule
    - DELETE /api/v1/email-automations/{id}/ - Delete rule
    - POST /api/v1/email-automations/{id}/toggle/ - Enable/disable
    """
    queryset = EmailAutomationRule.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'is_active']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailAutomationRuleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmailAutomationRuleCreateUpdateSerializer
        return EmailAutomationRuleDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('template').prefetch_related(
            'filter_obligation_types'
        )

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """
        POST /api/v1/email-automations/{id}/toggle/
        Toggle automation rule active status
        """
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save()

        serializer = EmailAutomationRuleDetailSerializer(rule)
        status_text = 'ενεργοποιήθηκε' if rule.is_active else 'απενεργοποιήθηκε'
        return Response({
            'message': f'Ο κανόνας {status_text}.',
            'rule': serializer.data
        })


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    REST API ViewSet for EmailLog (read-only)

    Endpoints:
    - GET /api/v1/email-logs/ - List (filter: client, status, date)
    - GET /api/v1/email-logs/{id}/ - Get single log entry
    """
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EmailPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EmailLogFilter
    ordering_fields = ['sent_at', 'status']
    ordering = ['-sent_at']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'client', 'obligation', 'template_used', 'sent_by'
        )


# ============================================
# EMAIL ACTIONS VIEWSET
# ============================================

class EmailActionsViewSet(viewsets.ViewSet):
    """
    ViewSet for email actions (send, bulk send, preview)

    Endpoints:
    - POST /api/v1/emails/send/ - Send email now
    - POST /api/v1/emails/send-bulk/ - Send to multiple clients
    - POST /api/v1/emails/preview/ - Preview email
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def send(self, request):
        """
        POST /api/v1/emails/send/
        Send email immediately
        """
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        recipients = data['to']
        subject = data['subject']
        body = data['body']
        template_id = data.get('template_id')
        client_id = data.get('client_id')
        obligation_id = data.get('obligation_id')

        # Get related objects
        template = None
        client = None
        obligation = None

        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id)
            except EmailTemplate.DoesNotExist:
                pass

        if obligation_id:
            try:
                obligation = MonthlyObligation.objects.select_related('client').get(id=obligation_id)
                client = obligation.client
            except MonthlyObligation.DoesNotExist:
                pass
        elif client_id:
            try:
                client = ClientProfile.objects.get(id=client_id)
            except ClientProfile.DoesNotExist:
                pass

        results = {
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for recipient_email in recipients:
            success, result = EmailService.send_email(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                client=client,
                obligation=obligation,
                template=template,
                user=request.user
            )

            if success:
                results['sent'] += 1
                results['details'].append({
                    'email': recipient_email,
                    'status': 'sent',
                    'message': 'Επιτυχία'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'email': recipient_email,
                    'status': 'failed',
                    'message': str(result)
                })

        return Response({
            'message': f'Στάλθηκαν {results["sent"]} από {len(recipients)} email.',
            'results': results
        })

    @action(detail=False, methods=['post'], url_path='send-bulk')
    def send_bulk(self, request):
        """
        POST /api/v1/emails/send-bulk/
        Send emails to multiple clients
        """
        serializer = SendBulkEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        client_ids = data['client_ids']
        template_id = data['template_id']
        schedule_at = data.get('schedule_at')
        extra_variables = data.get('variables', {})

        # Get template
        try:
            template = EmailTemplate.objects.get(id=template_id, is_active=True)
        except EmailTemplate.DoesNotExist:
            return Response(
                {'error': 'Το πρότυπο δεν βρέθηκε ή δεν είναι ενεργό.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get clients
        clients = ClientProfile.objects.filter(id__in=client_ids, is_active=True)
        if not clients.exists():
            return Response(
                {'error': 'Δεν βρέθηκαν ενεργοί πελάτες.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = {
            'sent': 0,
            'scheduled': 0,
            'skipped': 0,
            'failed': 0,
            'details': []
        }

        for client in clients:
            if not client.email:
                results['skipped'] += 1
                results['details'].append({
                    'client': client.eponimia,
                    'status': 'skipped',
                    'message': 'Δεν υπάρχει email'
                })
                continue

            # Render template
            subject, body = EmailService.render_template(
                template=template,
                client=client,
                extra_context=extra_variables,
                user=request.user
            )

            if schedule_at and schedule_at > timezone.now():
                # Schedule for later
                scheduled_email = ScheduledEmail.objects.create(
                    recipient_email=client.email,
                    recipient_name=client.eponimia,
                    client=client,
                    template=template,
                    subject=subject,
                    body_html=body,
                    send_at=schedule_at,
                    created_by=request.user
                )
                results['scheduled'] += 1
                results['details'].append({
                    'client': client.eponimia,
                    'status': 'scheduled',
                    'message': f'Προγραμματίστηκε για {schedule_at.strftime("%d/%m/%Y %H:%M")}'
                })
            else:
                # Send immediately
                success, result = EmailService.send_email(
                    recipient_email=client.email,
                    subject=subject,
                    body=body,
                    client=client,
                    template=template,
                    user=request.user
                )

                if success:
                    results['sent'] += 1
                    results['details'].append({
                        'client': client.eponimia,
                        'status': 'sent',
                        'message': f'Στάλθηκε στο {client.email}'
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'client': client.eponimia,
                        'status': 'failed',
                        'message': str(result)
                    })

        total = len(client_ids)
        return Response({
            'message': f'Επεξεργάστηκαν {total} πελάτες: {results["sent"]} στάλθηκαν, '
                      f'{results["scheduled"]} προγραμματίστηκαν, '
                      f'{results["skipped"]} παραλείφθηκαν, {results["failed"]} απέτυχαν.',
            'results': results
        })

    @action(detail=False, methods=['post'])
    def preview(self, request):
        """
        POST /api/v1/emails/preview/
        Preview email with template and optional client/obligation
        """
        serializer = PreviewEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        template_id = data['template_id']
        client_id = data.get('client_id')
        obligation_id = data.get('obligation_id')
        extra_variables = data.get('variables', {})

        # Get template
        try:
            template = EmailTemplate.objects.get(id=template_id)
        except EmailTemplate.DoesNotExist:
            return Response(
                {'error': 'Το πρότυπο δεν βρέθηκε.'},
                status=status.HTTP_404_NOT_FOUND
            )

        obligation = None
        client = None

        if obligation_id:
            try:
                obligation = MonthlyObligation.objects.select_related(
                    'client', 'obligation_type'
                ).get(id=obligation_id)
                client = obligation.client
            except MonthlyObligation.DoesNotExist:
                pass
        elif client_id:
            try:
                client = ClientProfile.objects.get(id=client_id)
            except ClientProfile.DoesNotExist:
                pass

        preview = EmailService.preview_email(
            template=template,
            obligation=obligation,
            client=client,
            extra_context=extra_variables,
            user=request.user
        )

        return Response(preview)
