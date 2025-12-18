"""
API endpoints για τις ρυθμίσεις του συστήματος αρχειοθέτησης.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import serializers

from .models import FilingSystemSettings


class FilingSystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer για FilingSystemSettings."""

    archive_root_display = serializers.SerializerMethodField()
    all_categories = serializers.SerializerMethodField()
    permanent_categories = serializers.SerializerMethodField()
    monthly_categories = serializers.SerializerMethodField()
    yearend_categories = serializers.SerializerMethodField()

    class Meta:
        model = FilingSystemSettings
        fields = [
            'id',
            # Βασικές ρυθμίσεις
            'archive_root',
            'archive_root_display',
            'use_network_storage',
            # Δομή φακέλων
            'folder_structure',
            'custom_folder_template',
            'use_greek_month_names',
            # Ειδικοί φάκελοι
            'enable_permanent_folder',
            'permanent_folder_name',
            'enable_yearend_folder',
            'yearend_folder_name',
            # Κατηγορίες
            'document_categories',
            'all_categories',
            'permanent_categories',
            'monthly_categories',
            'yearend_categories',
            # Ονοματολογία
            'file_naming_convention',
            # Πολιτική διατήρησης
            'retention_years',
            'auto_archive_years',
            'enable_retention_warnings',
            # Ασφάλεια
            'allowed_extensions',
            'max_file_size_mb',
            # Metadata
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_archive_root_display(self, obj):
        if obj.use_network_storage and obj.archive_root:
            return f"🌐 {obj.archive_root}"
        return "📁 Local (MEDIA_ROOT)"

    def get_all_categories(self, obj):
        return obj.get_all_categories()

    def get_permanent_categories(self, obj):
        categories = obj.get_all_categories()
        return {k: v for k, v in categories.items() if k in obj.get_permanent_folder_categories()}

    def get_monthly_categories(self, obj):
        categories = obj.get_all_categories()
        return {k: v for k, v in categories.items() if k in obj.get_monthly_folder_categories()}

    def get_yearend_categories(self, obj):
        categories = obj.get_all_categories()
        return {k: v for k, v in categories.items() if k in obj.get_yearend_folder_categories()}


class FilingSystemSettingsView(APIView):
    """
    GET: Λήψη ρυθμίσεων αρχειοθέτησης
    PUT/PATCH: Ενημέρωση ρυθμίσεων (μόνο admin)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings = FilingSystemSettings.get_settings()
        serializer = FilingSystemSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Μόνο διαχειριστές μπορούν να αλλάξουν τις ρυθμίσεις'},
                status=status.HTTP_403_FORBIDDEN
            )

        settings = FilingSystemSettings.get_settings()
        serializer = FilingSystemSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Μόνο διαχειριστές μπορούν να αλλάξουν τις ρυθμίσεις'},
                status=status.HTTP_403_FORBIDDEN
            )

        settings = FilingSystemSettings.get_settings()
        serializer = FilingSystemSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FolderStructurePreviewView(APIView):
    """
    GET: Προεπισκόπηση δομής φακέλων για έναν πελάτη.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from accounting.models import ClientProfile

        client_id = request.query_params.get('client_id')
        if not client_id:
            # Demo structure
            return Response({
                'structure': self._get_demo_structure()
            })

        try:
            client = ClientProfile.objects.get(pk=client_id)
            settings = FilingSystemSettings.get_settings()
            return Response({
                'structure': self._get_client_structure(client, settings)
            })
        except ClientProfile.DoesNotExist:
            return Response(
                {'error': 'Πελάτης δεν βρέθηκε'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_demo_structure(self):
        settings = FilingSystemSettings.get_settings()
        return {
            'name': '123456789_DEMO_ΕΤΑΙΡΕΙΑ',
            'type': 'client',
            'children': [
                {
                    'name': settings.permanent_folder_name,
                    'type': 'permanent',
                    'children': [
                        {'name': cat, 'type': 'category'}
                        for cat in settings.get_permanent_folder_categories()
                    ]
                },
                {
                    'name': '2025',
                    'type': 'year',
                    'children': [
                        {
                            'name': settings.get_month_folder_name(m),
                            'type': 'month',
                            'children': [
                                {'name': cat, 'type': 'category'}
                                for cat in settings.get_monthly_folder_categories()
                            ]
                        } for m in [1, 2, 3]
                    ] + [
                        {
                            'name': settings.yearend_folder_name,
                            'type': 'yearend',
                            'children': [
                                {'name': cat, 'type': 'category'}
                                for cat in settings.get_yearend_folder_categories()
                            ]
                        }
                    ]
                }
            ]
        }

    def _get_client_structure(self, client, settings):
        import re
        safe_name = re.sub(r'[^\w\s-]', '', client.eponimia)[:30]
        safe_name = safe_name.replace(' ', '_').strip('_')

        return {
            'name': f"{client.afm}_{safe_name}",
            'type': 'client',
            'client_id': client.id,
            'children': [
                {
                    'name': settings.permanent_folder_name,
                    'type': 'permanent',
                    'children': [
                        {'name': cat, 'type': 'category'}
                        for cat in settings.get_permanent_folder_categories()
                    ]
                },
                {
                    'name': '2025',
                    'type': 'year',
                    'children': [
                        {
                            'name': settings.get_month_folder_name(m),
                            'type': 'month',
                            'month': m,
                            'children': [
                                {'name': cat, 'type': 'category'}
                                for cat in settings.get_monthly_folder_categories()
                            ]
                        } for m in range(1, 13)
                    ] + [
                        {
                            'name': settings.yearend_folder_name,
                            'type': 'yearend',
                            'children': [
                                {'name': cat, 'type': 'category'}
                                for cat in settings.get_yearend_folder_categories()
                            ]
                        }
                    ]
                }
            ]
        }


class DocumentCategoriesView(APIView):
    """
    GET: Λήψη όλων των κατηγοριών εγγράφων με icons και colors.
    """
    permission_classes = [IsAuthenticated]

    # Category metadata
    CATEGORY_META = {
        # Permanent
        'registration': {'icon': 'building-2', 'color': '#8B5CF6', 'group': 'permanent'},
        'contracts': {'icon': 'file-signature', 'color': '#A855F7', 'group': 'permanent'},
        'licenses': {'icon': 'badge-check', 'color': '#9333EA', 'group': 'permanent'},
        'correspondence': {'icon': 'mail', 'color': '#7C3AED', 'group': 'permanent'},
        # Monthly
        'vat': {'icon': 'percent', 'color': '#EF4444', 'group': 'monthly'},
        'apd': {'icon': 'users', 'color': '#6366F1', 'group': 'monthly'},
        'myf': {'icon': 'file-spreadsheet', 'color': '#3B82F6', 'group': 'monthly'},
        'payroll': {'icon': 'wallet', 'color': '#EC4899', 'group': 'monthly'},
        'invoices_issued': {'icon': 'file-output', 'color': '#10B981', 'group': 'monthly'},
        'invoices_received': {'icon': 'file-input', 'color': '#14B8A6', 'group': 'monthly'},
        'bank': {'icon': 'landmark', 'color': '#0EA5E9', 'group': 'monthly'},
        'receipts': {'icon': 'receipt', 'color': '#22C55E', 'group': 'monthly'},
        # Yearend
        'e1': {'icon': 'file-text', 'color': '#F59E0B', 'group': 'yearend'},
        'e2': {'icon': 'home', 'color': '#F97316', 'group': 'yearend'},
        'e3': {'icon': 'bar-chart-3', 'color': '#FB923C', 'group': 'yearend'},
        'enfia': {'icon': 'building', 'color': '#FBBF24', 'group': 'yearend'},
        'balance': {'icon': 'scale', 'color': '#FCD34D', 'group': 'yearend'},
        'audit': {'icon': 'clipboard-check', 'color': '#FDE047', 'group': 'yearend'},
        # General
        'general': {'icon': 'folder', 'color': '#6B7280', 'group': 'monthly'},
        # Legacy
        'invoices': {'icon': 'receipt', 'color': '#10B981', 'group': 'monthly'},
        'tax': {'icon': 'landmark', 'color': '#F59E0B', 'group': 'yearend'},
        'efka': {'icon': 'shield', 'color': '#14B8A6', 'group': 'monthly'},
    }

    def get(self, request):
        settings = FilingSystemSettings.get_settings()
        all_categories = settings.get_all_categories()

        categories = []
        for code, label in all_categories.items():
            meta = self.CATEGORY_META.get(code, {'icon': 'folder', 'color': '#6B7280', 'group': 'monthly'})
            categories.append({
                'value': code,
                'label': label,
                'icon': meta['icon'],
                'color': meta['color'],
                'group': meta['group'],
            })

        # Group by type
        grouped = {
            'permanent': [c for c in categories if c['group'] == 'permanent'],
            'monthly': [c for c in categories if c['group'] == 'monthly'],
            'yearend': [c for c in categories if c['group'] == 'yearend'],
        }

        return Response({
            'categories': categories,
            'grouped': grouped,
        })
