from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, default=None, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])


class Product(SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Lot(SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lots')
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} (Product: {self.product.name})"

class Warehouse(SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Pallet(SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='pallets')
    lots = models.ManyToManyField(Lot, through='PalletLot', related_name='pallets')
    create_date = models.DateTimeField(default=timezone.now)
    in_date = models.DateTimeField(null=True, blank=True)
    out_date = models.DateTimeField(null=True, blank=True)
    is_out = models.BooleanField(default=False)
    defective = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PalletLot(models.Model):
    pallet = models.ForeignKey(Pallet, on_delete=models.CASCADE)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('pallet', 'lot') 

    def __str__(self):
        return f"Pallet: {self.pallet.name} - Lot: {self.lot.name}"

class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('MARK_OUT', 'Marcado como Salida'),
        ('MARK_DEFECTIVE', 'Marcado como Defectuoso'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']