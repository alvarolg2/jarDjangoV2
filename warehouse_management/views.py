
from argparse import Action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Prefetch
from django.utils import timezone
from .models import Product, Lot, Warehouse, Pallet, PalletLot, ActionLog
from .permissions import IsMemberOfCurrentTenant
from .serializers import (
    ProductSerializer, LotSerializer, WarehouseSerializer,
    PalletSerializer, PalletLotSerializer, ActionLogSerializer,
    LotWithPalletsInWarehouseSerializer,
    SyncProductSerializer, SyncWarehouseSerializer, SyncLotSerializer,
    SyncPalletSerializer, SyncPalletLotSerializer, SyncPayloadSerializer
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
    permission_classes = [IsAuthenticated, IsMemberOfCurrentTenant]

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
    permission_classes = [IsAuthenticated, IsMemberOfCurrentTenant]

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
    permission_classes = [IsAuthenticated, IsMemberOfCurrentTenant]

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

        relevant_pallets_qs = Pallet.objects.filter(
            warehouse=warehouse,
            is_out=False,
            defective=False
        )

        lots_in_warehouse_qs = Lot.objects.filter(
            pallets__warehouse=warehouse,
            pallets__is_out=False,
            pallets__defective=False 
        ).distinct().prefetch_related(
            Prefetch('pallets', queryset=relevant_pallets_qs, to_attr='cached_pallets_for_view')
        ).order_by('name')
        # pagination
        paginator = self.pagination_class() if self.pagination_class else None

        if paginator:
            page = paginator.paginate_queryset(lots_in_warehouse_qs, request, view=self)
            if page is not None: 
                serializer = LotWithPalletsInWarehouseSerializer(
                    page,
                    many=True,
                    context={'request': request, 'warehouse': warehouse}
                )
                return paginator.get_paginated_response(serializer.data)
            serializer_data = LotWithPalletsInWarehouseSerializer(
                [], 
                many=True,
                context={'request': request, 'warehouse': warehouse}
            ).data
            return paginator.get_paginated_response(serializer_data)
        
        serializer = LotWithPalletsInWarehouseSerializer(
            lots_in_warehouse_qs,
            many=True,
            context={'request': request, 'warehouse': warehouse}
        )
        return Response(serializer.data)

class PalletViewSet(viewsets.ModelViewSet):
    queryset = Pallet.objects.all().order_by('-create_date')
    serializer_class = PalletSerializer
    permission_classes = [IsAuthenticated, IsMemberOfCurrentTenant]

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
    permission_classes = [IsAuthenticated, IsMemberOfCurrentTenant]


class SyncView(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfCurrentTenant]

    def get(self, request):
        last_sync = request.query_params.get('last_sync')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 1000))

        products_qs = Product.all_objects.all()
        warehouses_qs = Warehouse.all_objects.all()
        lots_qs = Lot.all_objects.all()
        pallets_qs = Pallet.all_objects.all()
        pallet_lots_qs = PalletLot.objects.all()

        if last_sync:
            products_qs = products_qs.filter(
                models.Q(create_date__gt=last_sync) | 
                models.Q(updated_at__gt=last_sync) | 
                models.Q(deleted_at__gt=last_sync)
            )
            warehouses_qs = warehouses_qs.filter(
                models.Q(create_date__gt=last_sync) | 
                models.Q(updated_at__gt=last_sync) | 
                models.Q(deleted_at__gt=last_sync)
            )
            lots_qs = lots_qs.filter(
                models.Q(create_date__gt=last_sync) | 
                models.Q(updated_at__gt=last_sync) | 
                models.Q(deleted_at__gt=last_sync)
            )
            pallets_qs = pallets_qs.filter(
                models.Q(create_date__gt=last_sync) | 
                models.Q(updated_at__gt=last_sync) | 
                models.Q(deleted_at__gt=last_sync)
            )
            pallet_lots_qs = pallet_lots_qs.filter(
                models.Q(pallet__create_date__gt=last_sync) |
                models.Q(pallet__updated_at__gt=last_sync) |
                models.Q(pallet__deleted_at__gt=last_sync) |
                models.Q(lot__create_date__gt=last_sync) |
                models.Q(lot__updated_at__gt=last_sync) |
                models.Q(lot__deleted_at__gt=last_sync)
            )

        start = (page - 1) * page_size
        end = start + page_size

        data = {
            'products': SyncProductSerializer(products_qs[start:end], many=True).data,
            'warehouses': SyncWarehouseSerializer(warehouses_qs[start:end], many=True).data,
            'lots': SyncLotSerializer(lots_qs[start:end], many=True).data,
            'pallets': SyncPalletSerializer(pallets_qs[start:end], many=True).data,
            'pallet_lots': SyncPalletLotSerializer(pallet_lots_qs.distinct()[start:end], many=True).data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_products': products_qs.count(),
                'total_warehouses': warehouses_qs.count(),
                'total_lots': lots_qs.count(),
                'total_pallets': pallets_qs.count(),
                'total_pallet_lots': pallet_lots_qs.distinct().count(),
            },
            'server_time': timezone.now().isoformat(),
        }
        return Response(data)

    def post(self, request):
        serializer = SyncPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            stats = self._sync_products(data.get('products', []))
            stats.update(self._sync_warehouses(data.get('warehouses', [])))
            stats.update(self._sync_lots(data.get('lots', [])))
            stats.update(self._sync_pallets(data.get('pallets', [])))
            stats.update(self._sync_pallet_lots(data.get('pallet_lots', [])))

        stats['server_time'] = timezone.now().isoformat()
        return Response(stats)

    def _sync_products(self, items):
        if not items:
            return {'products': {'created': 0, 'updated': 0, 'deleted': 0}}

        existing_ids = set(Product.all_objects.values_list('id', flat=True))
        now = timezone.now()

        to_create = []
        to_update = []

        for item in items:
            if item['id'] not in existing_ids:
                to_create.append(Product(
                    id=item['id'],
                    name=item.get('name', ''),
                    description=item.get('description'),
                    deleted_at=item.get('deleted_at')
                ))
            else:
                existing = Product.all_objects.get(id=item['id'])
                existing.name = item.get('name', '')
                existing.description = item.get('description')
                existing.deleted_at = item.get('deleted_at')
                existing.updated_at = now
                to_update.append(existing)

        if to_create:
            Product.all_objects.bulk_create(to_create, ignore_conflicts=True)

        if to_update:
            Product.all_objects.bulk_update(
                to_update,
                ['name', 'description', 'deleted_at', 'updated_at'],
                batch_size=1000
            )

        return {'products': {
            'created': len(to_create),
            'updated': len(to_update),
            'deleted': 0
        }}

    def _sync_warehouses(self, items):
        if not items:
            return {'warehouses': {'created': 0, 'updated': 0, 'deleted': 0}}

        existing_ids = set(Warehouse.all_objects.values_list('id', flat=True))
        now = timezone.now()

        to_create = []
        to_update = []

        for item in items:
            if item['id'] not in existing_ids:
                to_create.append(Warehouse(
                    id=item['id'],
                    name=item.get('name', ''),
                    address=item.get('address'),
                    deleted_at=item.get('deleted_at')
                ))
            else:
                existing = Warehouse.all_objects.get(id=item['id'])
                existing.name = item.get('name', '')
                existing.address = item.get('address')
                existing.deleted_at = item.get('deleted_at')
                existing.updated_at = now
                to_update.append(existing)

        if to_create:
            Warehouse.all_objects.bulk_create(to_create, ignore_conflicts=True)

        if to_update:
            Warehouse.all_objects.bulk_update(
                to_update,
                ['name', 'address', 'deleted_at', 'updated_at'],
                batch_size=1000
            )

        return {'warehouses': {
            'created': len(to_create),
            'updated': len(to_update),
            'deleted': 0
        }}

    def _sync_lots(self, items):
        if not items:
            return {'lots': {'created': 0, 'updated': 0, 'deleted': 0}}

        existing_ids = set(Lot.all_objects.values_list('id', flat=True))
        now = timezone.now()

        to_create = []
        to_update = []

        for item in items:
            if item['id'] not in existing_ids:
                to_create.append(Lot(
                    id=item['id'],
                    name=item.get('name', ''),
                    product_id=item.get('product'),
                    deleted_at=item.get('deleted_at')
                ))
            else:
                existing = Lot.all_objects.get(id=item['id'])
                existing.name = item.get('name', '')
                existing.product_id = item.get('product')
                existing.deleted_at = item.get('deleted_at')
                existing.updated_at = now
                to_update.append(existing)

        if to_create:
            Lot.all_objects.bulk_create(to_create, ignore_conflicts=True)

        if to_update:
            Lot.all_objects.bulk_update(
                to_update,
                ['name', 'product_id', 'deleted_at', 'updated_at'],
                batch_size=1000
            )

        return {'lots': {
            'created': len(to_create),
            'updated': len(to_update),
            'deleted': 0
        }}

    def _sync_pallets(self, items):
        if not items:
            return {'pallets': {'created': 0, 'updated': 0, 'deleted': 0}}

        existing_ids = set(Pallet.all_objects.values_list('id', flat=True))
        now = timezone.now()

        to_create = []
        to_update = []

        for item in items:
            defaults = {
                'name': item.get('name', ''),
                'warehouse_id': item.get('warehouse'),
                'is_out': item.get('is_out', False),
                'defective': item.get('defective', False),
                'in_date': item.get('in_date'),
                'out_date': item.get('out_date'),
                'deleted_at': item.get('deleted_at'),
            }

            if item['id'] not in existing_ids:
                to_create.append(Pallet(id=item['id'], **defaults))
            else:
                existing = Pallet.all_objects.get(id=item['id'])
                for key, value in defaults.items():
                    setattr(existing, key, value)
                existing.updated_at = now
                to_update.append(existing)

        if to_create:
            Pallet.all_objects.bulk_create(to_create, ignore_conflicts=True)

        if to_update:
            Pallet.all_objects.bulk_update(
                to_update,
                ['name', 'warehouse_id', 'is_out', 'defective', 'in_date', 'out_date', 'deleted_at', 'updated_at'],
                batch_size=1000
            )

        return {'pallets': {
            'created': len(to_create),
            'updated': len(to_update),
            'deleted': 0
        }}

    def _sync_pallet_lots(self, items):
        if not items:
            return {'pallet_lots': {'created': 0, 'deleted': 0}}

        existing_pairs = set(
            PalletLot.objects.values_list('pallet_id', 'lot_id')
        )

        to_create = []
        for item in items:
            pair = (item['pallet'], item['lot'])
            if pair not in existing_pairs:
                to_create.append(PalletLot(pallet_id=item['pallet'], lot_id=item['lot']))

        if to_create:
            PalletLot.objects.bulk_create(to_create, ignore_conflicts=True)

        return {'pallet_lots': {
            'created': len(to_create),
            'deleted': 0
        }}