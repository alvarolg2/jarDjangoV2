# jarDjangoV2
Backend for JAR app

**jarDjangoV2** es un sistema de gestión de almacenes (WMS) robusto construido con Django, que utiliza una arquitectura **multi-tenant** para aislar los datos de diferentes clientes mediante esquemas de base de datos independientes.

## 🚀 Tecnologías Principales

* **Framework:** Django 5.2.1.
* **API:** Django REST Framework 3.16.0.
* **Multi-tenancy:** `django-tenants` 3.8.0 para aislamiento a nivel de esquema en PostgreSQL.
* **Base de Datos:** PostgreSQL (vía `psycopg2-binary`).
* **Configuración:** `python-dotenv` para gestión de variables de entorno.

## 🏗️ Arquitectura Multi-tenant

El proyecto divide las aplicaciones en dos categorías para manejar el aislamiento de datos:

* **Shared Apps (Esquema Público):** Contiene la gestión de inquilinos (`tenants`), dominios y la configuración global del sistema.
* **Tenant Apps (Esquemas Privados):** Incluye la lógica de negocio de `warehouse_management`, permitiendo que cada cliente tenga sus propios productos, lotes y almacenes de forma privada.

## 📦 Módulos del Sistema

### Gestión de Almacén (`warehouse_management`)
* **Productos y Lotes:** Control de inventario organizado por productos y sus respectivos lotes de producción.
* **Almacenes y Pallets:** Gestión física de ubicaciones y unidades de carga (Pallets).
* **Log de Acciones:** Registro detallado de auditoría que rastrea creaciones, actualizaciones, eliminaciones y movimientos de mercancía (salidas o estados defectuosos).

### Gestión de Clientes (`tenants`)
* **Tenants y Dominios:** Configuración de los esquemas de base de datos y sus URLs asociadas.
* **Membresías:** Vinculación de usuarios específicos con uno o más tenants, garantizando que el personal solo acceda a la información autorizada.

## 🔐 Seguridad y Autenticación

* **Token Authentication:** Acceso seguro mediante tokens de DRF.
* **Tenant Permissions:** El sistema incluye un permiso personalizado (`IsMemberOfCurrentTenant`) que verifica que el usuario autenticado pertenezca realmente al tenant que está intentando consultar.

## 🛠️ Instalación y Configuración

1. **Clonar el repositorio e instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configurar variables de entorno: Crea un archivo .env basado en la configuración de settings.py:**

* DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

* SECRET_KEY, DEBUG, ALLOWED_HOSTS

3. **Ejecutar migraciones y configuración inicial:**

```bash
python manage.py migrate_schemas --shared
python manage.py setup_initial_tenants
```
Nota: El comando setup_initial_tenants creará automáticamente el tenant público (localhost) y un cliente de ejemplo (alpha.localhost).

## 📡 Endpoints Principales
* **Autenticación: POST /api/v1/get-token/ (Devuelve token y lista de tenants disponibles para el usuario).**

* **Productos: GET/POST /api/v1/warehouse/products/.**

* **Pallets por Lote: GET /api/v1/warehouse/warehouses/{id}/pallets-by-lot/.**

* **Auditoría: GET /api/v1/warehouse/action-logs/.**
