from rest_framework.permissions import BasePermission
from tenants.models import TenantMembership 

class IsMemberOfCurrentTenant(BasePermission):
    """
    Permite el acceso solo si el usuario autenticado es miembro
    del tenant actualmente activo (identificado por django-tenants).
    """
    message = "No tienes permiso para acceder a este tenant."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request, 'tenant') or not request.tenant:
            return False

        return TenantMembership.objects.filter(user=request.user, tenant=request.tenant).exists()