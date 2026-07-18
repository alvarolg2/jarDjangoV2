from django.contrib import admin

from jar_backend import __version__

admin.site.site_header = f"JAR Backend v{__version__}"
admin.site.site_title = f"JAR v{__version__}"
admin.site.index_title = "Administración"
