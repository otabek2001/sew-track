"""
Custom exceptions for SEW-TRACK project.
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class BusinessLogicError(APIException):
    """Base exception for business logic errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A business logic error occurred.'
    default_code = 'business_logic_error'


class ValidationError(BusinessLogicError):
    """Exception for validation errors."""
    default_detail = 'Validation failed.'
    default_code = 'validation_error'


class ResourceNotFoundError(APIException):
    """Exception when a resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'resource_not_found'


class PermissionDeniedError(APIException):
    """Exception when user doesn't have permission."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class ConflictError(APIException):
    """Exception for conflicts (e.g., duplicate records)."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'A conflict occurred.'
    default_code = 'conflict'

