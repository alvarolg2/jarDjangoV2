from rest_framework import serializers
from .models import Tenant, Domain

class DomainForTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['domain', 'is_primary']

class TenantSimpleSerializer(serializers.ModelSerializer):

    all_domains = DomainForTenantSerializer(source='domains', many=True, read_only=True)


    class Meta:
        model = Tenant
        fields = ['id', 'name', 'schema_name', 'all_domains']