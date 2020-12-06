from django.db import models
from base.models import BaseModel
from jsonfield import JSONField
from django.conf import settings

from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location=settings.PATH_UPLOAD_CONFIGS)


class ConfigUpload(BaseModel):
    parsed_data = JSONField()
    config_yml_file = models.FileField(upload_to='./vars_yaml', blank=True, null=True)
    config_json_file = models.FileField(upload_to='./vars_json', blank=True, null=True)
