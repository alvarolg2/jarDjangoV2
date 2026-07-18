# jar_backend/urls.py (o el nombre de tu proyecto)
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from tenants.views import CustomTokenObtainPairView

from jar_backend.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/health/', health_check, name='health_check'),
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/warehouse/', include('warehouse_management.urls')),
]