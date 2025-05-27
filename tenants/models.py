# tenants/models.py
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.conf import settings

class Tenant(TenantMixin):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class Domain(DomainMixin):
    def __str__(self):
        return self.domain

class TenantMembership(models.Model): 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='memberships')
    is_active_for_user = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'tenant')

    def __str__(self):
        return f"{self.user.username} en {self.tenant.name}"