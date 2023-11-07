from rest_framework.permissions import BasePermission, SAFE_METHODS
from store.models import Customer


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsMyCustomerProfileOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return 1
        return obj.user_id == request.user.id


class ViewCustomerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')
