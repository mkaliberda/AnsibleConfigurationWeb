from django.contrib import admin
from sites.models import Site


class SiteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Site._meta.fields]

admin.site.register(Site, SiteAdmin)