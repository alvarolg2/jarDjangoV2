# tenants/admin.py
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Tenant, Domain, TenantMembership

class UserMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 1
    autocomplete_fields = ['user']
@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'created_on')
    inlines = [UserMembershipInline]