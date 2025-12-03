# -*- coding: utf-8 -*-
"""
API Response Helpers
====================
Standardized API response format for React frontend integration.

Usage:
    from common.utils.api_response import api_success, api_error

    # Success response
    return api_success(data={'user': serializer.data}, message='User created')

    # Error response
    return api_error('Validation failed', errors={'email': ['Invalid format']})
"""
from django.http import JsonResponse


def api_success(data=None, message=None, status=200):
    """
    Return a standardized success response.

    Args:
        data: The response payload (dict, list, or any JSON-serializable value)
        message: Optional success message
        status: HTTP status code (default: 200)

    Returns:
        JsonResponse with format:
        {
            "success": true,
            "data": <data>,
            "message": <message>
        }
    """
    return JsonResponse({
        'success': True,
        'data': data,
        'message': message
    }, status=status)


def api_error(message, errors=None, status=400):
    """
    Return a standardized error response.

    Args:
        message: Error message string
        errors: Optional dict of field-specific errors
        status: HTTP status code (default: 400)

    Returns:
        JsonResponse with format:
        {
            "success": false,
            "error": <message>,
            "errors": <errors>
        }
    """
    return JsonResponse({
        'success': False,
        'error': message,
        'errors': errors
    }, status=status)


def api_paginated(queryset, serializer_class, request, page_size=50):
    """
    Return a standardized paginated response.

    Args:
        queryset: Django QuerySet to paginate
        serializer_class: DRF serializer class for the queryset items
        request: Django request object
        page_size: Number of items per page (default: 50)

    Returns:
        JsonResponse with format:
        {
            "success": true,
            "data": {
                "items": [...],
                "total": <total_count>,
                "page": <current_page>,
                "page_size": <page_size>,
                "total_pages": <total_pages>
            },
            "message": null
        }
    """
    from django.core.paginator import Paginator, EmptyPage

    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    serializer = serializer_class(page_obj.object_list, many=True)

    return api_success(data={
        'items': serializer.data,
        'total': paginator.count,
        'page': page_obj.number,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })
