from django.db import models
from base.models import BaseModel
from jsonfield import JSONField
from django.conf import settings
from .types import PlaybookServiceTypes

from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location=settings.PATH_UPLOAD_CONFIGS)


class ConfigUpload(BaseModel):
    AUDIT = 'audit'
    DEPLOY = 'deploy'
    CUSTOMIZE = 'customize'

    TAGS = (
        (AUDIT, 'Audit'),
        (DEPLOY, 'Deploy'),
        (CUSTOMIZE, 'Customize'),
    )

    parsed_data = JSONField()
    config_yml_file = models.FileField(upload_to='./vars_yaml', blank=True, null=True)
    config_json_file = models.FileField(upload_to='./vars_json', blank=True, null=True)
    service_type = models.CharField(choices=PlaybookServiceTypes.choices(), max_length=64, blank=True, null=True)
    tag = models.CharField(choices=TAGS, default=AUDIT, max_length=64, blank=True, null=True)
    site = models.ForeignKey('sites.Site', on_delete=models.SET_NULL, blank=True, null=True)
