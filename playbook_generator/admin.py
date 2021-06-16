from django.contrib import admin
from playbook_generator.models import ConfigUpload, StaticVarsFile, StaticVarsValue, StaticSiteVars


class ConfigUploadAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConfigUpload._meta.fields]

admin.site.register(ConfigUpload, ConfigUploadAdmin)


class StaticVarsFileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StaticVarsValue._meta.fields]

admin.site.register(StaticVarsValue, StaticVarsFileAdmin)


class StaticSiteVarsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StaticSiteVars._meta.fields]

admin.site.register(StaticSiteVars, StaticSiteVarsAdmin)
