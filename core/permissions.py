"""
Custom permissions for SEW-TRACK project.
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Assume object has 'user' or 'employee' field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'employee'):
            return obj.employee.user == request.user
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to everyone,
    but only admins can modify.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsStaffUser(permissions.BasePermission):
    """
    Permission to only allow staff users.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

