# En gestion_almacen/admin.py
from django.contrib import admin
from .models import Product, Lot, Warehouse, Pallet, PalletLot, ActionLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date')
    search_fields = ('name',)

@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'create_date')
    list_filter = ('product',)
    search_fields = ('name', 'product__name')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'create_date')
    search_fields = ('name',)

class PalletLotInline(admin.TabularInline):
    model = PalletLot
    extra = 1 

@admin.register(Pallet)
class PalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'is_out', 'defective', 'create_date', 'out_date')
    list_filter = ('warehouse', 'is_out', 'defective')
    search_fields = ('name',)
    inlines = [PalletLotInline]

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'content_object_display', 'timestamp')
    list_filter = ('action_type', 'user', 'content_type')
    readonly_fields = ('user', 'action_type', 'content_type', 'object_id', 'timestamp', 'description')

    def content_object_display(self, obj):
        if obj.content_type and obj.object_id:
            ModelClass = obj.content_type.model_class()
            if ModelClass:
                try:
                    return ModelClass.objects.get(pk=obj.object_id)
                except ModelClass.DoesNotExist:
                    return f"Objeto eliminado (ID: {obj.object_id})"
        return "-"
    content_object_display.short_description = 'Objeto Afectado'