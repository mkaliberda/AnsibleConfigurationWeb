from django.db import models
from base.models import BaseModel


class Site(BaseModel):
    name = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
      return f'{self.name}'
