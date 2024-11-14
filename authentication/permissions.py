# permissions.py
from rest_framework import permissions

from authentication.constants import ROLE_ADMIN, ROLE_STAFF


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == ROLE_ADMIN


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == ROLE_STAFF


IsAdminOrStaff = IsAdmin | IsStaff
