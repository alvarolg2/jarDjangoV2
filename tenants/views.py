from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import TenantMembership
from .serializers import TenantSimpleSerializer

class CustomAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        user_tenants_data = []
        memberships = TenantMembership.objects.filter(user=user).select_related(
            'tenant'
        ).prefetch_related(
            'tenant__domains'
        )

        for membership in memberships:
            
            tenant_data = TenantSimpleSerializer(membership.tenant).data
            user_tenants_data.append(tenant_data)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'available_tenants': user_tenants_data
        })