from django.db import models
from base.models import BaseModel
from jsonfield import JSONField
from django.conf import settings

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
    tag = models.CharField(choices=TAGS, default=AUDIT, max_length=64, blank=True, null=True)
