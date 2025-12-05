# -*- coding: utf-8 -*-
"""
accounting/api_email.py
Author: Claude
Description: REST API for email sending - templates, send, obligation notifications
"""

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import (
    ClientProfile, MonthlyObligation, EmailTemplate, EmailLog, ClientDocument
)
from .services.email_service import EmailService


# ============================================
# EMAIL SERIALIZERS
# ============================================

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for EmailTemplate"""
    obligation_type_name = serializers.CharField(
        source='obligation_type.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'description', 'subject', 'body_html',
            'obligation_type', 'obligation_type_name',
            'is_active', 'created_at', 'updated_at'
        ]


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog"""
    template_name = serializers.CharField(
        source='template_used.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = EmailLog
        fields = [
            'id', 'recipient_email', 'recipient_name',
            'client', 'obligation', 'template_used', 'template_name',
            'subject', 'body', 'status', 'error_message',
            'sent_at', 'sent_by'
        ]


class SendEmailSerializer(serializers.Serializer):
    """Serializer for sending email"""
    client_id = serializers.IntegerField()
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField()
    template_id = serializers.IntegerField(required=False, allow_null=True)
    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )

    def validate_client_id(self, value):
        try:
            client = ClientProfile.objects.get(id=value)
            if not client.email:
                raise serializers.ValidationError('Ο πελάτης δεν έχει email.')
        except ClientProfile.DoesNotExist:
            raise serializers.ValidationError('Ο πελάτης δεν βρέθηκε.')
        return value

    def validate_template_id(self, value):
        if value:
            try:
                EmailTemplate.objects.get(id=value, is_active=True)
            except EmailTemplate.DoesNotExist:
                raise serializers.ValidationError('Το πρότυπο email δεν βρέθηκε.')
        return value


class SendObligationNoticeSerializer(serializers.Serializer):
    """Serializer for sending obligation notice"""
    obligation_id = serializers.IntegerField()
    template_type = serializers.ChoiceField(
        choices=['reminder', 'completion', 'overdue'],
        default='completion'
    )
    template_id = serializers.IntegerField(required=False, allow_null=True)
    include_attachment = serializers.BooleanField(default=True)
    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )

    def validate_obligation_id(self, value):
        try:
            obligation = MonthlyObligation.objects.get(id=value)
            if not obligation.client.email:
                raise serializers.ValidationError('Ο πελάτης δεν έχει email.')
        except MonthlyObligation.DoesNotExist:
            raise serializers.ValidationError('Η υποχρέωση δεν βρέθηκε.')
        return value


class CompleteAndNotifySerializer(serializers.Serializer):
    """Serializer for complete obligation and send notification"""
    document_id = serializers.IntegerField(required=False, allow_null=True)
    file = serializers.FileField(required=False, allow_null=True)
    send_email = serializers.BooleanField(default=True)
    email_template_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    time_spent = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )


class BulkCompleteNotifySerializer(serializers.Serializer):
    """Serializer for bulk complete with notification"""
    obligation_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    send_notifications = serializers.BooleanField(default=False)


# ============================================
# EMAIL TEMPLATE ENDPOINTS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_templates(request):
    """
    GET /api/v1/email/templates/
    List all active email templates
    """
    templates = EmailTemplate.objects.filter(is_active=True).order_by('name')
    serializer = EmailTemplateSerializer(templates, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_template_detail(request, template_id):
    """
    GET /api/v1/email/templates/{id}/
    Get single email template with preview
    """
    try:
        template = EmailTemplate.objects.get(id=template_id, is_active=True)
    except EmailTemplate.DoesNotExist:
        return Response(
            {'error': 'Το πρότυπο δεν βρέθηκε.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = EmailTemplateSerializer(template)
    return Response({
        **serializer.data,
        'available_variables': EmailTemplate.get_available_variables()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_email(request):
    """
    POST /api/v1/email/preview/
    Preview email with template and context

    Body: {
        "template_id": 1,
        "obligation_id": 123  (optional)
        "client_id": 456  (if no obligation_id)
    }
    """
    template_id = request.data.get('template_id')
    obligation_id = request.data.get('obligation_id')
    client_id = request.data.get('client_id')

    if not template_id:
        return Response(
            {'error': 'Απαιτείται template_id.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        template = EmailTemplate.objects.get(id=template_id, is_active=True)
    except EmailTemplate.DoesNotExist:
        return Response(
            {'error': 'Το πρότυπο δεν βρέθηκε.'},
            status=status.HTTP_404_NOT_FOUND
        )

    obligation = None
    client = None

    if obligation_id:
        try:
            obligation = MonthlyObligation.objects.get(id=obligation_id)
            client = obligation.client
        except MonthlyObligation.DoesNotExist:
            return Response(
                {'error': 'Η υποχρέωση δεν βρέθηκε.'},
                status=status.HTTP_404_NOT_FOUND
            )
    elif client_id:
        try:
            client = ClientProfile.objects.get(id=client_id)
        except ClientProfile.DoesNotExist:
            return Response(
                {'error': 'Ο πελάτης δεν βρέθηκε.'},
                status=status.HTTP_404_NOT_FOUND
            )

    preview = EmailService.preview_email(
        template=template,
        obligation=obligation,
        client=client,
        user=request.user
    )

    return Response(preview)


# ============================================
# SEND EMAIL ENDPOINTS
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email(request):
    """
    POST /api/v1/email/send/
    Send email to client

    Body: {
        "client_id": 123,
        "subject": "Θέμα",
        "body": "Κείμενο email (HTML)",
        "template_id": 1,  (optional)
        "attachment_ids": [1, 2, 3]  (optional - document IDs)
    }
    """
    serializer = SendEmailSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    client_id = serializer.validated_data['client_id']
    subject = serializer.validated_data['subject']
    body = serializer.validated_data['body']
    template_id = serializer.validated_data.get('template_id')
    attachment_ids = serializer.validated_data.get('attachment_ids', [])

    client = ClientProfile.objects.get(id=client_id)
    template = None
    if template_id:
        template = EmailTemplate.objects.get(id=template_id)

    # Get attachments
    attachments = []
    if attachment_ids:
        documents = ClientDocument.objects.filter(
            id__in=attachment_ids,
            client=client
        )
        for doc in documents:
            if doc.file:
                attachments.append(doc.file)

    # Send email
    success, result = EmailService.send_email(
        recipient_email=client.email,
        subject=subject,
        body=body,
        client=client,
        template=template,
        user=request.user,
        attachments=attachments
    )

    if success:
        return Response({
            'success': True,
            'message': f'Το email στάλθηκε στο {client.email}.',
            'email_log_id': result.id
        })
    else:
        return Response({
            'success': False,
            'message': 'Αποτυχία αποστολής email.',
            'error': str(result)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_obligation_notice(request):
    """
    POST /api/v1/email/send-obligation-notice/
    Send obligation reminder/completion/overdue notice

    Body: {
        "obligation_id": 123,
        "template_type": "completion",  // reminder | completion | overdue
        "template_id": 1,  (optional - override template)
        "include_attachment": true,
        "attachment_ids": [1, 2]  (optional - additional document IDs)
    }
    """
    serializer = SendObligationNoticeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obligation_id = serializer.validated_data['obligation_id']
    template_type = serializer.validated_data['template_type']
    template_id = serializer.validated_data.get('template_id')
    include_attachment = serializer.validated_data['include_attachment']
    attachment_ids = serializer.validated_data.get('attachment_ids', [])

    obligation = MonthlyObligation.objects.get(id=obligation_id)
    client = obligation.client

    # Get template
    if template_id:
        template = EmailTemplate.objects.get(id=template_id, is_active=True)
    else:
        # Find appropriate template based on type
        template = EmailTemplate.get_template_for_obligation(obligation)
        if not template:
            return Response({
                'success': False,
                'message': 'Δεν βρέθηκε πρότυπο email.'
            }, status=status.HTTP_400_BAD_REQUEST)

    # Render template
    subject, body = EmailService.render_template(
        template=template,
        obligation=obligation,
        user=request.user
    )

    # Collect attachments
    attachments = []
    if include_attachment and obligation.attachment:
        attachments.append(obligation.attachment)

    if attachment_ids:
        documents = ClientDocument.objects.filter(
            id__in=attachment_ids,
            client=client
        )
        for doc in documents:
            if doc.file:
                attachments.append(doc.file)

    # Send email
    success, result = EmailService.send_email(
        recipient_email=client.email,
        subject=subject,
        body=body,
        client=client,
        obligation=obligation,
        template=template,
        user=request.user,
        attachments=attachments
    )

    if success:
        return Response({
            'success': True,
            'message': f'Το email στάλθηκε στο {client.email}.',
            'email_log_id': result.id
        })
    else:
        return Response({
            'success': False,
            'message': 'Αποτυχία αποστολής email.',
            'error': str(result)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# COMPLETE AND NOTIFY ENDPOINT
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_and_notify(request, obligation_id):
    """
    POST /api/v1/obligations/{id}/complete-and-notify/
    Mark obligation as complete, optionally attach document and send email

    Body: {
        "document_id": 123,  (optional - attach existing document)
        "file": <file>,  (optional - upload new document, multipart)
        "send_email": true,
        "email_template_id": 1,  (optional)
        "notes": "Σημειώσεις",
        "time_spent": 1.5
    }
    """
    from django.utils import timezone
    import os

    try:
        obligation = MonthlyObligation.objects.get(id=obligation_id)
    except MonthlyObligation.DoesNotExist:
        return Response(
            {'error': 'Η υποχρέωση δεν βρέθηκε.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if obligation.status == 'completed':
        return Response(
            {'error': 'Η υποχρέωση είναι ήδη ολοκληρωμένη.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    client = obligation.client
    document = None
    email_sent = False
    email_error = None

    # Handle document attachment
    document_id = request.data.get('document_id')
    if document_id:
        try:
            document = ClientDocument.objects.get(id=document_id, client=client)
            document.obligation = obligation
            document.save()
        except ClientDocument.DoesNotExist:
            return Response(
                {'error': 'Το έγγραφο δεν βρέθηκε.'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Handle file upload
    if 'file' in request.FILES:
        uploaded_file = request.FILES['file']

        # Validate file
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png']
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext not in allowed_extensions:
            return Response(
                {'error': f'Μη επιτρεπτός τύπος αρχείου.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if uploaded_file.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'Το αρχείο είναι μεγαλύτερο από 10MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine category
        category = 'general'
        if obligation.obligation_type:
            type_code = obligation.obligation_type.code.upper()
            if 'ΦΠΑ' in type_code:
                category = 'vat'
            elif 'ΜΥΦ' in type_code:
                category = 'myf'
            elif 'ΑΠΔ' in type_code:
                category = 'payroll'
            elif 'Ε1' in type_code or 'Ε3' in type_code:
                category = 'tax'

        document = ClientDocument.objects.create(
            client=client,
            obligation=obligation,
            file=uploaded_file,
            document_category=category,
            description=f'Υποχρέωση {obligation.obligation_type.name} {obligation.month:02d}/{obligation.year}'
        )

    # Mark obligation as completed
    obligation.status = 'completed'
    obligation.completed_date = timezone.now().date()
    obligation.completed_by = request.user

    if request.data.get('notes'):
        obligation.notes = request.data.get('notes')

    if request.data.get('time_spent'):
        try:
            obligation.time_spent = float(request.data.get('time_spent'))
        except (ValueError, TypeError):
            pass

    obligation.save()

    # Send email notification if requested
    send_email = request.data.get('send_email', True)
    if send_email and client.email:
        template_id = request.data.get('email_template_id')

        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id, is_active=True)
            except EmailTemplate.DoesNotExist:
                template = EmailTemplate.get_template_for_obligation(obligation)
        else:
            template = EmailTemplate.get_template_for_obligation(obligation)

        if template:
            # Collect attachments
            attachments = []
            if document and document.file:
                attachments.append(document.file)
            elif obligation.attachment:
                attachments.append(obligation.attachment)

            # Render and send
            subject, body = EmailService.render_template(
                template=template,
                obligation=obligation,
                user=request.user
            )

            success, result = EmailService.send_email(
                recipient_email=client.email,
                subject=subject,
                body=body,
                client=client,
                obligation=obligation,
                template=template,
                user=request.user,
                attachments=attachments
            )

            email_sent = success
            if not success:
                email_error = str(result)

    # Prepare response
    from .api_obligations import ObligationDetailSerializer
    obligation_serializer = ObligationDetailSerializer(
        obligation, context={'request': request}
    )

    response_data = {
        'success': True,
        'message': 'Η υποχρέωση ολοκληρώθηκε.',
        'obligation': obligation_serializer.data,
    }

    if document:
        from .api_documents import DocumentSerializer
        response_data['document'] = DocumentSerializer(
            document, context={'request': request}
        ).data

    if send_email:
        response_data['email_sent'] = email_sent
        if email_error:
            response_data['email_error'] = email_error

    return Response(response_data)


# ============================================
# BULK COMPLETE WITH NOTIFICATIONS
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_complete_with_notify(request):
    """
    POST /api/v1/obligations/bulk-complete-notify/
    Mark multiple obligations as completed and optionally send notifications

    Body: {
        "obligation_ids": [1, 2, 3],
        "send_notifications": true
    }
    """
    serializer = BulkCompleteNotifySerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obligation_ids = serializer.validated_data['obligation_ids']
    send_notifications = serializer.validated_data['send_notifications']

    from django.utils import timezone

    # Get obligations that can be completed
    obligations = MonthlyObligation.objects.filter(
        id__in=obligation_ids,
        status__in=['pending', 'overdue']
    ).select_related('client', 'obligation_type')

    completed_count = 0
    email_results = {
        'sent': 0,
        'failed': 0,
        'skipped': 0,
        'details': []
    }

    for obligation in obligations:
        # Mark as completed
        obligation.status = 'completed'
        obligation.completed_date = timezone.now().date()
        obligation.completed_by = request.user
        obligation.save()
        completed_count += 1

        # Send notification if requested
        if send_notifications:
            client = obligation.client
            if not client.email:
                email_results['skipped'] += 1
                email_results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'skipped',
                    'message': 'Ο πελάτης δεν έχει email'
                })
                continue

            template = EmailTemplate.get_template_for_obligation(obligation)
            if not template:
                email_results['failed'] += 1
                email_results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'failed',
                    'message': 'Δεν βρέθηκε πρότυπο'
                })
                continue

            success, result = EmailService.send_obligation_completion_email(
                obligation=obligation,
                user=request.user,
                include_attachment=True
            )

            if success:
                email_results['sent'] += 1
                email_results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'sent',
                    'message': f'Στάλθηκε στο {client.email}'
                })
            else:
                email_results['failed'] += 1
                email_results['details'].append({
                    'obligation_id': obligation.id,
                    'client': client.eponimia,
                    'status': 'failed',
                    'message': str(result)
                })

    response_data = {
        'success': True,
        'message': f'{completed_count} υποχρεώσεις ολοκληρώθηκαν.',
        'completed_count': completed_count,
    }

    if send_notifications:
        response_data['email_results'] = email_results

    return Response(response_data)


# ============================================
# EMAIL HISTORY
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_history(request):
    """
    GET /api/v1/email/history/
    List sent emails with filtering

    Query params:
    - client_id: filter by client
    - obligation_id: filter by obligation
    - status: filter by status (sent, failed, pending)
    - page: page number
    - page_size: items per page
    """
    queryset = EmailLog.objects.all().select_related(
        'client', 'obligation', 'template_used', 'sent_by'
    ).order_by('-sent_at')

    # Apply filters
    client_id = request.query_params.get('client_id')
    obligation_id = request.query_params.get('obligation_id')
    email_status = request.query_params.get('status')

    if client_id:
        queryset = queryset.filter(client_id=client_id)
    if obligation_id:
        queryset = queryset.filter(obligation_id=obligation_id)
    if email_status:
        queryset = queryset.filter(status=email_status)

    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    emails = queryset[start:end]

    serializer = EmailLogSerializer(emails, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'results': serializer.data
    })
