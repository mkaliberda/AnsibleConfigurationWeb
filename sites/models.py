from enum import unique
from django.db import models
from base.models import BaseModel
from playbook_generator.models.types import PlaybookServiceTypes

class Site(BaseModel):
    name = models.CharField(max_length=512, blank=True, null=True)
    service_type = models.CharField(choices=PlaybookServiceTypes.choices(), max_length=64, blank=True, null=True)

    def __str__(self):
      return f'{self.name}'

    class Meta:
      unique_together = ('service_type', 'name',)
