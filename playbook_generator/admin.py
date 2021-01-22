from django.contrib import admin
from playbook_generator.models import ConfigUpload, StaticVarsFile, StaticVarsValue


class ConfigUploadAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConfigUpload._meta.fields]

admin.site.register(ConfigUpload, ConfigUploadAdmin)


class StaticVarsFileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StaticVarsValue._meta.fields]

admin.site.register(StaticVarsValue, StaticVarsFileAdmin)
