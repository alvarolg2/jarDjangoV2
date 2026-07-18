from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import TenantMembership
from .serializers import TenantSimpleSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        user_tenants_data = []
        memberships = TenantMembership.objects.filter(user=user).select_related(
            'tenant'
        ).prefetch_related(
            'tenant__domains'
        )

        for membership in memberships:
            tenant_data = TenantSimpleSerializer(membership.tenant).data
            user_tenants_data.append(tenant_data)

        data['user_id'] = user.pk
        data['username'] = user.username
        data['available_tenants'] = user_tenants_data

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer