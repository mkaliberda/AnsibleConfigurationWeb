from django.db import models
from base.models import BaseModel
from jsonfield import JSONField


class ConfigUpload(BaseModel):
    parsed_data = JSONField()
    config_yml_file = models.FileField()
