# -*- coding: utf-8 -*-
"""
accounting/api_obligation_settings.py
Author: Claude
Description: REST API for Obligation Settings Management (CRUD)

Endpoints:
- ObligationType CRUD: /api/v1/settings/obligation-types/
- ObligationProfile CRUD: /api/v1/settings/obligation-profiles/
- ObligationGroup CRUD: /api/v1/settings/obligation-groups/
"""

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    ObligationType,
    ObligationProfile,
    ObligationGroup,
)


# ============================================
# SERIALIZERS
# ============================================

class ObligationTypeSettingsSerializer(serializers.ModelSerializer):
    """Full serializer for ObligationType in settings"""
    profile_name = serializers.CharField(source='profile.name', read_only=True, default=None)
    exclusion_group_name = serializers.CharField(source='exclusion_group.name', read_only=True, default=None)

    class Meta:
        model = ObligationType
        fields = [
            'id',
            'code',
            'name',
            'description',
            'frequency',
            'deadline_type',
            'deadline_day',
            'applicable_months',
            'exclusion_group',
            'exclusion_group_name',
            'profile',
            'profile_name',
            'priority',
            'is_active',
        ]
        extra_kwargs = {
            'code': {'required': True},
            'name': {'required': True},
        }

    def validate_code(self, value):
        """Ensure code is unique (case-insensitive)"""
        qs = ObligationType.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ο κωδικός υπάρχει ήδη.')
        return value.upper()

    def validate_deadline_day(self, value):
        """Validate deadline day is within valid range"""
        if value is not None and (value < 1 or value > 31):
            raise serializers.ValidationError('Η ημέρα πρέπει να είναι μεταξύ 1-31.')
        return value


class ObligationTypeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    profile_name = serializers.CharField(source='profile.name', read_only=True, default=None)
    exclusion_group_name = serializers.CharField(source='exclusion_group.name', read_only=True, default=None)

    class Meta:
        model = ObligationType
        fields = [
            'id',
            'code',
            'name',
            'frequency',
            'deadline_type',
            'deadline_day',
            'profile',
            'profile_name',
            'exclusion_group',
            'exclusion_group_name',
            'is_active',
        ]


class ObligationProfileSettingsSerializer(serializers.ModelSerializer):
    """Full serializer for ObligationProfile in settings"""
    obligation_types_count = serializers.SerializerMethodField()
    obligation_types = serializers.SerializerMethodField()

    class Meta:
        model = ObligationProfile
        fields = [
            'id',
            'name',
            'description',
            'obligation_types_count',
            'obligation_types',
        ]
        extra_kwargs = {
            'name': {'required': True},
        }

    def get_obligation_types_count(self, obj):
        return obj.obligations.filter(is_active=True).count()

    def get_obligation_types(self, obj):
        """Return list of obligation types linked to this profile"""
        types = obj.obligations.filter(is_active=True).values('id', 'name', 'code')
        return list(types)

    def validate_name(self, value):
        """Ensure name is unique"""
        qs = ObligationProfile.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Το όνομα υπάρχει ήδη.')
        return value


class ObligationGroupSettingsSerializer(serializers.ModelSerializer):
    """Full serializer for ObligationGroup (exclusion groups) in settings"""
    obligation_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ObligationType.objects.filter(is_active=True),
        source='obligationtype_set',
        required=False
    )
    obligation_type_names = serializers.SerializerMethodField()

    class Meta:
        model = ObligationGroup
        fields = [
            'id',
            'name',
            'description',
            'obligation_types',
            'obligation_type_names',
        ]
        extra_kwargs = {
            'name': {'required': True},
        }

    def get_obligation_type_names(self, obj):
        """Return list of obligation type names in this group"""
        return list(obj.obligationtype_set.filter(is_active=True).values_list('name', flat=True))

    def validate_name(self, value):
        """Ensure name is unique"""
        qs = ObligationGroup.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Το όνομα υπάρχει ήδη.')
        return value

    def create(self, validated_data):
        obligation_types = validated_data.pop('obligationtype_set', [])
        instance = super().create(validated_data)
        if obligation_types:
            for ot in obligation_types:
                ot.exclusion_group = instance
                ot.save()
        return instance

    def update(self, instance, validated_data):
        obligation_types = validated_data.pop('obligationtype_set', None)
        instance = super().update(instance, validated_data)

        if obligation_types is not None:
            # Clear existing types from this group
            instance.obligationtype_set.update(exclusion_group=None)
            # Set new types
            for ot in obligation_types:
                ot.exclusion_group = instance
                ot.save()

        return instance


# ============================================
# VIEWSETS
# ============================================

class ObligationTypeSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ObligationType CRUD operations

    GET    /api/v1/settings/obligation-types/       - List all types
    POST   /api/v1/settings/obligation-types/       - Create new type
    GET    /api/v1/settings/obligation-types/{id}/  - Get single type
    PUT    /api/v1/settings/obligation-types/{id}/  - Update type
    DELETE /api/v1/settings/obligation-types/{id}/  - Delete type
    """
    queryset = ObligationType.objects.all().select_related('profile', 'exclusion_group')
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'frequency', 'profile', 'exclusion_group']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['priority', 'name', 'code', 'is_active']
    ordering = ['priority', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ObligationTypeListSerializer
        return ObligationTypeSettingsSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete by setting is_active=False, or hard delete if requested"""
        instance = self.get_object()
        force_delete = request.query_params.get('force', 'false').lower() == 'true'

        if force_delete:
            # Check if type is used in any MonthlyObligation
            from .models import MonthlyObligation
            if MonthlyObligation.objects.filter(obligation_type=instance).exists():
                return Response(
                    {'error': 'Δεν μπορεί να διαγραφεί γιατί χρησιμοποιείται σε υποχρεώσεις.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
        else:
            instance.is_active = False
            instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active obligation types"""
        queryset = self.queryset.filter(is_active=True)
        serializer = ObligationTypeListSerializer(queryset, many=True)
        return Response(serializer.data)


class ObligationProfileSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ObligationProfile CRUD operations

    GET    /api/v1/settings/obligation-profiles/       - List all profiles
    POST   /api/v1/settings/obligation-profiles/       - Create new profile
    GET    /api/v1/settings/obligation-profiles/{id}/  - Get single profile
    PUT    /api/v1/settings/obligation-profiles/{id}/  - Update profile
    DELETE /api/v1/settings/obligation-profiles/{id}/  - Delete profile
    """
    queryset = ObligationProfile.objects.all().prefetch_related('obligations')
    serializer_class = ObligationProfileSettingsSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

    def destroy(self, request, *args, **kwargs):
        """Delete profile, but unlink obligation types first"""
        instance = self.get_object()

        # Check if profile is used by any ClientObligation
        from .models import ClientObligation
        if ClientObligation.objects.filter(obligation_profiles=instance).exists():
            force_delete = request.query_params.get('force', 'false').lower() == 'true'
            if not force_delete:
                return Response(
                    {'error': 'Το profile χρησιμοποιείται από πελάτες. Χρησιμοποιήστε force=true για να διαγραφεί.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Unlink obligation types before deleting
        instance.obligations.update(profile=None)
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def types(self, request, pk=None):
        """Get all obligation types linked to this profile"""
        profile = self.get_object()
        types = profile.obligations.filter(is_active=True)
        serializer = ObligationTypeListSerializer(types, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_types(self, request, pk=None):
        """Add obligation types to this profile"""
        profile = self.get_object()
        type_ids = request.data.get('obligation_type_ids', [])

        if not type_ids:
            return Response(
                {'error': 'Δεν δόθηκαν τύποι υποχρεώσεων.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        types = ObligationType.objects.filter(id__in=type_ids, is_active=True)
        types.update(profile=profile)

        return Response({
            'success': True,
            'message': f'Προστέθηκαν {types.count()} τύποι στο profile.'
        })

    @action(detail=True, methods=['post'])
    def remove_types(self, request, pk=None):
        """Remove obligation types from this profile"""
        profile = self.get_object()
        type_ids = request.data.get('obligation_type_ids', [])

        if not type_ids:
            return Response(
                {'error': 'Δεν δόθηκαν τύποι υποχρεώσεων.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        types = ObligationType.objects.filter(id__in=type_ids, profile=profile)
        types.update(profile=None)

        return Response({
            'success': True,
            'message': f'Αφαιρέθηκαν {types.count()} τύποι από το profile.'
        })


class ObligationGroupSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ObligationGroup (exclusion groups) CRUD operations

    GET    /api/v1/settings/obligation-groups/       - List all groups
    POST   /api/v1/settings/obligation-groups/       - Create new group
    GET    /api/v1/settings/obligation-groups/{id}/  - Get single group
    PUT    /api/v1/settings/obligation-groups/{id}/  - Update group
    DELETE /api/v1/settings/obligation-groups/{id}/  - Delete group
    """
    queryset = ObligationGroup.objects.all().prefetch_related('obligationtype_set')
    serializer_class = ObligationGroupSettingsSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

    def destroy(self, request, *args, **kwargs):
        """Delete group, but unlink obligation types first"""
        instance = self.get_object()

        # Unlink obligation types before deleting
        instance.obligationtype_set.update(exclusion_group=None)
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def types(self, request, pk=None):
        """Get all obligation types in this exclusion group"""
        group = self.get_object()
        types = group.obligationtype_set.filter(is_active=True)
        serializer = ObligationTypeListSerializer(types, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_types(self, request, pk=None):
        """Set which obligation types belong to this group"""
        group = self.get_object()
        type_ids = request.data.get('obligation_type_ids', [])

        # Clear existing types from this group
        group.obligationtype_set.update(exclusion_group=None)

        # Set new types
        if type_ids:
            ObligationType.objects.filter(id__in=type_ids, is_active=True).update(exclusion_group=group)

        return Response({
            'success': True,
            'message': 'Οι τύποι υποχρεώσεων ενημερώθηκαν.'
        })
