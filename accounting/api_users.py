# -*- coding: utf-8 -*-
"""
User Management API for LogistikoCRM
=====================================
CRUD endpoints for managing users (admin only).
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import serializers

User = get_user_model()


# ==============================================================================
# SERIALIZERS
# ==============================================================================

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password', 'password_confirm', 'is_staff', 'is_active']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Οι κωδικοί δεν ταιριάζουν.'})

        # Validate password strength
        try:
            validate_password(attrs.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users."""
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password', 'is_staff', 'is_active']

    def validate_password(self, value):
        if value:
            try:
                validate_password(value)
            except ValidationError as e:
                raise serializers.ValidationError(list(e.messages))
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


# ==============================================================================
# VIEWS
# ==============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_list(request):
    """
    GET /api/v1/users/
    List all users (admin only).
    """
    users = User.objects.all().order_by('-date_joined')
    serializer = UserListSerializer(users, many=True)

    return Response({
        'success': True,
        'count': users.count(),
        'users': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_create(request):
    """
    POST /api/v1/users/
    Create a new user (admin only).
    """
    serializer = UserCreateSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': f'Ο χρήστης "{user.username}" δημιουργήθηκε επιτυχώς.',
            'user': UserListSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_detail(request, user_id):
    """
    GET /api/v1/users/{id}/
    Get user details (admin only).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ο χρήστης δεν βρέθηκε.'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = UserListSerializer(user)
    return Response({
        'success': True,
        'user': serializer.data
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_update(request, user_id):
    """
    PUT/PATCH /api/v1/users/{id}/
    Update a user (admin only).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ο χρήστης δεν βρέθηκε.'
        }, status=status.HTTP_404_NOT_FOUND)

    # Prevent editing superuser if not superuser
    if user.is_superuser and not request.user.is_superuser:
        return Response({
            'success': False,
            'error': 'Δεν έχετε δικαίωμα να επεξεργαστείτε αυτόν τον χρήστη.'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = UserUpdateSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': f'Ο χρήστης "{user.username}" ενημερώθηκε επιτυχώς.',
            'user': UserListSerializer(user).data
        })

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_delete(request, user_id):
    """
    DELETE /api/v1/users/{id}/
    Delete a user (admin only).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ο χρήστης δεν βρέθηκε.'
        }, status=status.HTTP_404_NOT_FOUND)

    # Prevent self-deletion
    if user.id == request.user.id:
        return Response({
            'success': False,
            'error': 'Δεν μπορείτε να διαγράψετε τον εαυτό σας.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Prevent deleting superuser if not superuser
    if user.is_superuser and not request.user.is_superuser:
        return Response({
            'success': False,
            'error': 'Δεν έχετε δικαίωμα να διαγράψετε αυτόν τον χρήστη.'
        }, status=status.HTTP_403_FORBIDDEN)

    username = user.username
    user.delete()

    return Response({
        'success': True,
        'message': f'Ο χρήστης "{username}" διαγράφηκε επιτυχώς.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_toggle_active(request, user_id):
    """
    POST /api/v1/users/{id}/toggle-active/
    Toggle user active status (admin only).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ο χρήστης δεν βρέθηκε.'
        }, status=status.HTTP_404_NOT_FOUND)

    # Prevent self-deactivation
    if user.id == request.user.id:
        return Response({
            'success': False,
            'error': 'Δεν μπορείτε να απενεργοποιήσετε τον εαυτό σας.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = not user.is_active
    user.save()

    status_text = 'ενεργοποιήθηκε' if user.is_active else 'απενεργοποιήθηκε'

    return Response({
        'success': True,
        'message': f'Ο χρήστης "{user.username}" {status_text}.',
        'user': UserListSerializer(user).data
    })
