# jar_backend/urls.py (o el nombre de tu proyecto)
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/get-token/', obtain_auth_token, name='api_token_auth'),
    path('api/v1/warehouse/', include('warehouse_management.urls')),
]