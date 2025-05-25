from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, LotViewSet, WarehouseViewSet,
    PalletViewSet, ActionLogViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'lots', LotViewSet, basename='lot')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'pallets', PalletViewSet, basename='pallet')
router.register(r'action-logs', ActionLogViewSet, basename='actionlog')

urlpatterns = [
    path('', include(router.urls)),
]