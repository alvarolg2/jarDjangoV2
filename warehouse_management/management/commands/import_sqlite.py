import sqlite3
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from warehouse_management.models import Product, Warehouse, Lot, Pallet, PalletLot


class Command(BaseCommand):
    help = 'Importa datos desde una base de datos SQLite (warehouse_transport.db) a Django'

    def add_arguments(self, parser):
        parser.add_argument(
            'db_path',
            type=str,
            help='Ruta al archivo SQLite de origen (warehouse_transport.db)',
        )
        parser.add_argument(
            '--tenant',
            type=str,
            default=None,
            help='Nombre del tenant al que importar los datos (requerido si usas django_tenants)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Tamaño de lote para bulk operations (default: 1000)',
        )

    def handle(self, *args, **options):
        db_path = options['db_path']
        tenant_name = options['tenant']
        batch_size = options['batch_size']

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
        except Exception as e:
            raise CommandError(f'No se pudo abrir la base de datos: {e}')

        if tenant_name:
            from django.db import connection
            from tenants.models import Tenant
            try:
                tenant = Tenant.objects.get(name=tenant_name)
            except Tenant.DoesNotExist:
                raise CommandError(f'Tenant "{tenant_name}" no existe')
            connection.set_tenant(tenant)
            self.stdout.write(self.style.SUCCESS(f'Usando tenant: {tenant_name}'))

        self.stdout.write(f'Importando desde: {db_path}')

        with transaction.atomic():
            counts = {}
            counts['product'] = self._import_products(conn, batch_size)
            counts['warehouse'] = self._import_warehouses(conn, batch_size)
            counts['lot'] = self._import_lots(conn, batch_size)
            counts['pallet'] = self._import_pallets(conn, batch_size)
            counts['pallet_lot'] = self._import_pallet_lots(conn, batch_size)

        conn.close()

        self.stdout.write(self.style.SUCCESS('Importacion completada:'))
        for table, count in counts.items():
            self.stdout.write(f'  {table}: {count} registros')

    def _import_products(self, conn, batch_size):
        rows = list(conn.execute('SELECT * FROM product'))
        to_create = []
        
        for row in rows:
            to_create.append(Product(
                id=row['id'],
                name=row['name'] or '',
                description=row['description'] if 'description' in row.keys() else None,
            ))
        
        Product.all_objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)
        self.stdout.write(f'  Productos importados: {len(to_create)}')
        return len(to_create)

    def _import_warehouses(self, conn, batch_size):
        rows = list(conn.execute('SELECT * FROM warehouse'))
        to_create = []
        
        for row in rows:
            to_create.append(Warehouse(
                id=row['id'],
                name=row['name'] or '',
                address=row['address'],
            ))
        
        Warehouse.all_objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)
        self.stdout.write(f'  Almacenes importados: {len(to_create)}')
        return len(to_create)

    def _import_lots(self, conn, batch_size):
        rows = list(conn.execute('SELECT * FROM lot'))
        to_create = []
        
        for row in rows:
            to_create.append(Lot(
                id=row['id'],
                name=row['name'] or '',
                product_id=row['product'],
            ))
        
        Lot.all_objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)
        self.stdout.write(f'  Lotes importados: {len(to_create)}')
        return len(to_create)

    def _import_pallets(self, conn, batch_size):
        rows = list(conn.execute('SELECT * FROM pallet'))
        to_create = []
        
        for row in rows:
            defaults = {
                'id': row['id'],
                'name': row['name'] or '',
                'warehouse_id': row['warehouse'],
                'is_out': bool(row['is_out']),
                'defective': bool(row['defective']),
            }
            
            date_val = None
            if 'in_date' in row.keys():
                date_val = row['in_date']
            elif 'date' in row.keys():
                date_val = row['date']
            
            if date_val:
                defaults['in_date'] = date_val
            
            if 'out_date' in row.keys() and row['out_date']:
                defaults['out_date'] = row['out_date']
            
            to_create.append(Pallet(**defaults))
        
        Pallet.all_objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)
        self.stdout.write(f'  Pallets importados: {len(to_create)}')
        return len(to_create)

    def _import_pallet_lots(self, conn, batch_size):
        rows = list(conn.execute('SELECT * FROM pallet_lot'))
        to_create = []
        
        for row in rows:
            to_create.append(PalletLot(
                pallet_id=row['id_pallet'],
                lot_id=row['id_lot'],
            ))
        
        PalletLot.objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)
        self.stdout.write(f'  Pallet-Lot relations importadas: {len(to_create)}')
        return len(to_create)
