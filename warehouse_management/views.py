
from argparse import Action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from .models import Product, Lot, Warehouse, Pallet, PalletLot, ActionLog
from .serializers import (
    ProductSerializer, LotSerializer, WarehouseSerializer,
    PalletSerializer, PalletLotSerializer, ActionLogSerializer,
    LotWithPalletsInWarehouseSerializer
)

def log_action(user, action_type, instance, description=""):
    ActionLog.objects.create(
        user=user,
        action_type=action_type,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        description=description
    )

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-create_date')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'CREATE', instance, f"Producto '{instance.name}' creado.")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'UPDATE', instance, f"Producto '{instance.name}' actualizado.")

    def perform_destroy(self, instance):
        description = f"Producto '{instance.name}' (ID: {instance.pk}) eliminado."
        content_type_instance = ContentType.objects.get_for_model(instance)
        object_id_instance = instance.pk
        instance.delete()
        ActionLog.objects.create(
            user=self.request.user,
            action_type='DELETE',
            content_type=content_type_instance,
            object_id=object_id_instance,
            description=description
        )


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all().order_by('-create_date')
    serializer_class = LotSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'CREATE', instance, f"Lote '{instance.name}' creado para producto '{instance.product.name}'.")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'UPDATE', instance, f"Lote '{instance.name}' actualizado.")

    def perform_destroy(self, instance):
        description = f"Lote '{instance.name}' (ID: {instance.pk}) eliminado."
        content_type_instance = ContentType.objects.get_for_model(instance)
        object_id_instance = instance.pk
        instance.delete()
        ActionLog.objects.create(
            user=self.request.user, action_type='DELETE',
            content_type=content_type_instance, object_id=object_id_instance,
            description=description
        )

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('-create_date')
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'CREATE', instance, f"Almacén '{instance.name}' creado.")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'UPDATE', instance, f"Almacén '{instance.name}' actualizado.")

    def perform_destroy(self, instance):
        description = f"Almacén '{instance.name}' (ID: {instance.pk}) eliminado."
        content_type_instance = ContentType.objects.get_for_model(instance)
        object_id_instance = instance.pk
        instance.delete()
        ActionLog.objects.create(
            user=self.request.user, action_type='DELETE',
            content_type=content_type_instance, object_id=object_id_instance,
            description=description
        )
    @action(detail=True, methods=['get'], url_path='pallets-by-lot')
    def pallets_grouped_by_lot(self, request, pk=None):
        warehouse = self.get_object()
        relevant_pallets_prefetch = Prefetch(
            'pallets',
            queryset=Pallet.objects.filter(warehouse=warehouse, is_out=False),
            to_attr='cached_pallets_in_warehouse'
        )

        lots_in_warehouse = Lot.objects.filter(
            pallets__warehouse=warehouse,
            pallets__is_out=False
        ).distinct().prefetch_related(
            relevant_pallets_prefetch
        ).order_by('name')

        serializer = LotWithPalletsInWarehouseSerializer(
            lots_in_warehouse,
            many=True,
            context={'request': request, 'warehouse': warehouse}
        )
        return Response(serializer.data)

class PalletViewSet(viewsets.ModelViewSet):
    queryset = Pallet.objects.all().order_by('-create_date')
    serializer_class = PalletSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'CREATE', instance, f"Pallet '{instance.name}' creado.")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'UPDATE', instance, f"Pallet '{instance.name}' actualizado.")
        if 'is_out' in serializer.validated_data and serializer.validated_data['is_out'] and not serializer.instance.is_out:
             log_action(self.request.user, 'MARK_OUT', instance, f"Pallet '{instance.name}' marcado como salida.")
        if 'defective' in serializer.validated_data and serializer.validated_data['defective'] and not serializer.instance.defective:
             log_action(self.request.user, 'MARK_DEFECTIVE', instance, f"Pallet '{instance.name}' marcado como defectuoso.")


    def perform_destroy(self, instance):
        description = f"Pallet '{instance.name}' (ID: {instance.pk}) eliminado."
        content_type_instance = ContentType.objects.get_for_model(instance)
        object_id_instance = instance.pk
        instance.delete()
        ActionLog.objects.create(
            user=self.request.user, action_type='DELETE',
            content_type=content_type_instance, object_id=object_id_instance,
            description=description
        )


class ActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActionLog.objects.all().order_by('-timestamp')
    serializer_class = ActionLogSerializer
    permission_classes = [IsAuthenticated]