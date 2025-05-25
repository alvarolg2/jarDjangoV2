# warehouse_management/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Lot, Warehouse, Pallet, PalletLot, ActionLog
from django.contrib.contenttypes.models import ContentType

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = fields

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']
        read_only_fields = fields

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'create_date']
        read_only_fields = ['create_date']

class LotSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Lot
        fields = ['id', 'name', 'product', 'product_name', 'create_date']
        read_only_fields = ['create_date', 'product_name']

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'address', 'create_date']
        read_only_fields = ['create_date']

class PalletLotSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.name', read_only=True)
    product_name = serializers.CharField(source='lot.product.name', read_only=True)

    class Meta:
        model = PalletLot
        fields = ['id', 'pallet', 'lot', 'lot_name', 'product_name'] 
        read_only_fields = ['pallet', 'lot_name', 'product_name']

class PalletSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True, allow_null=True)
    lots_ids = serializers.PrimaryKeyRelatedField(
        queryset=Lot.objects.all(),
        source='lots',
        many=True,
        write_only=True,
        allow_empty=True
    )
    pallet_lots_details = PalletLotSerializer(source='palletlot_set', many=True, read_only=True)


    class Meta:
        model = Pallet
        fields = [
            'id', 'name', 'warehouse', 'warehouse_name',
            'lots_ids',
            'pallet_lots_details',
            'create_date', 'in_date', 'out_date', 'is_out', 'defective'
        ]
        read_only_fields = ['create_date', 'warehouse_name', 'pallet_lots_details']


class ActionLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    content_type = ContentTypeSerializer(read_only=True) 
    affected_object_str = serializers.SerializerMethodField()

    class Meta:
        model = ActionLog
        fields = ['id', 'user', 'action_type', 'timestamp', 'content_type', 'object_id', 'affected_object_str', 'description']
        read_only_fields = fields

    def get_affected_object_str(self, obj):
        if obj.content_type and obj.object_id:
            ModelClass = obj.content_type.model_class()
            if ModelClass:
                try:
                    return str(ModelClass.objects.get(pk=obj.object_id))
                except ModelClass.DoesNotExist:
                    return f"Object ({obj.content_type.model}) ID: {obj.object_id} (Delete)"
        return None

class SimplePalletForGroupingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pallet
        # Solo los campos que quieres mostrar para cada pallet individual
        fields = ['id', 'name', 'in_date', 'is_out', 'defective']

class LotWithPalletsInWarehouseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    # Lista de pallets (activos y no defectuosos) en este almacén para este lote
    pallets_active = serializers.SerializerMethodField()
    # Conteo de pallets no defectuosos (y activos)
    count_pallets_ok = serializers.SerializerMethodField()
    # Conteo de pallets defectuosos (pero activos)
    count_pallets_defective = serializers.SerializerMethodField()

    class Meta:
        model = Lot
        fields = [
            'id', 'name', 'product', 'product_name',
            'pallets_active', # La lista de pallets buenos
            'count_pallets_ok',
            'count_pallets_defective'
        ]

    def _get_filtered_pallets_for_lot_in_warehouse(self, lot_instance, warehouse_instance):
        """
        Helper interno para obtener los pallets de un lote en un almacén específico.
        Aquí asumimos que queremos pallets que NO han salido (is_out=False).
        """
        if not warehouse_instance:
            return Pallet.objects.none() # Devuelve un queryset vacío si no hay almacén

        # Si usaste 'to_attr' en prefetch_related en la vista, podrías intentar accederlo aquí
        # if hasattr(lot_instance, 'prefetched_pallets_for_warehouse_and_lot'):
        #     return lot_instance.prefetched_pallets_for_warehouse_and_lot

        # Si no, filtramos aquí. El prefetch_related general en la vista ayudará.
        return Pallet.objects.filter(
            lots=lot_instance,
            warehouse=warehouse_instance,
            is_out=False # Condición: Pallets que no han salido (activos en almacén)
        )

    def get_pallets_active(self, obj):
        # 'obj' es la instancia del Lote
        warehouse = self.context.get('warehouse')
        all_pallets_for_lot_in_warehouse = self._get_filtered_pallets_for_lot_in_warehouse(obj, warehouse)
        
        # Filtramos para los que NO son defectuosos para esta lista específica
        active_non_defective_pallets = all_pallets_for_lot_in_warehouse.filter(defective=False).order_by('create_date')
        return SimplePalletForGroupingSerializer(active_non_defective_pallets, many=True).data

    def get_count_pallets_ok(self, obj):
        # 'obj' es la instancia del Lote
        warehouse = self.context.get('warehouse')
        all_pallets_for_lot_in_warehouse = self._get_filtered_pallets_for_lot_in_warehouse(obj, warehouse)
        return all_pallets_for_lot_in_warehouse.filter(defective=False).count()

    def get_count_pallets_defective(self, obj):
        # 'obj' es la instancia del Lote
        warehouse = self.context.get('warehouse')
        all_pallets_for_lot_in_warehouse = self._get_filtered_pallets_for_lot_in_warehouse(obj, warehouse)
        return all_pallets_for_lot_in_warehouse.filter(defective=True).count()