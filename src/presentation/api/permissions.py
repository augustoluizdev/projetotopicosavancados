"""
Custom Permissions for Event Management API.
"""
from rest_framework.permissions import BasePermission


class IsEventOrganizer(BasePermission):
    """
    Custom permission to only allow event organizers to edit events.
    This is a placeholder - implement based on your authentication system.
    """

    def has_object_permission(self, request, view, obj):
        # Implement organizer check logic here
        # For now, allow all authenticated users
        return request.user and request.user.is_authenticated


class CanRegisterForEvent(BasePermission):
    """
    Custom permission to check if user can register for events.
    """

    def has_permission(self, request, view):
        # Implement registration permission logic here
        # For now, allow all authenticated users
        return request.user and request.user.is_authenticated