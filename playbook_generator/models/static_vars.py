from django.db import models
from base.models import BaseModel
from jsonfield import JSONField
from django.conf import settings
from .types import PlaybookServiceTypes
from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location=settings.PATH_UPLOAD_CONFIGS)


class StaticVarsFile(BaseModel):
    config_yaml_file = models.FileField( blank=True, null=True)
    tag = models.CharField(choices=PlaybookServiceTypes.choices(), max_length=64, blank=True, null=True)


class StaticVarsValue(BaseModel):
  service_type = models.CharField(choices=PlaybookServiceTypes.choices(), max_length=64, blank=True, null=True)
  key = models.CharField(max_length=64, blank=True, null=True)
  value = models.CharField(max_length=64, blank=True, null=True)
