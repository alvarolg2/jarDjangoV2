from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):

    def handle(self, *args, **options):
        Tenant = apps.get_model('tenants', 'Tenant')
        Domain = apps.get_model('tenants', 'Domain')

        self.stdout.write(self.style.SUCCESS('Configurando tenants y dominios iniciales...'))

        # Tenant public
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Tenant'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Tenant '{public_tenant.name}' creado."))
        else:
            self.stdout.write(f"Tenant '{public_tenant.name}' ya existía.")

        domain_public, d_created = Domain.objects.get_or_create(
            domain='localhost',
            tenant=public_tenant,
            defaults={'is_primary': True}
        )
        if d_created:
            self.stdout.write(self.style.SUCCESS(f"Dominio '{domain_public.domain}' para tenant '{public_tenant.name}' creado/asegurado."))
        else:
            self.stdout.write(f"Dominio '{domain_public.domain}' para tenant '{public_tenant.name}' ya existía.")


        # Tenant example
        cliente_alpha_name = 'Cliente Alpha SAS'
        cliente_alpha_schema = 'alpha'
        cliente_alpha_domain = 'alpha.localhost'

        cliente_alpha, created = Tenant.objects.get_or_create(
            schema_name=cliente_alpha_schema,
            defaults={'name': cliente_alpha_name}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Tenant '{cliente_alpha.name}' (schema: {cliente_alpha_schema}) creado."))
        else:
            self.stdout.write(f"Tenant '{cliente_alpha.name}' (schema: {cliente_alpha_schema}) ya existía.")

        domain_alpha, d_created = Domain.objects.get_or_create(
            domain=cliente_alpha_domain,
            tenant=cliente_alpha,
            defaults={'is_primary': True}
        )
        if d_created:
            self.stdout.write(self.style.SUCCESS(f"Dominio '{domain_alpha.domain}' para tenant '{cliente_alpha.name}' creado."))
        else:
            self.stdout.write(f"Dominio '{domain_alpha.domain}' para tenant '{cliente_alpha.name}' ya existía.")

        self.stdout.write(self.style.SUCCESS('Configuración inicial de tenants completada.'))