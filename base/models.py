import uuid
from django.db import models

# Create your models here.


class BaseModel(models.Model):
    """
        Base abstract model
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    is_delete = models.BooleanField(default=False)

    @staticmethod
    def is_valid_uuid(val):
        """
        check is_valid_uuid
        :param val:
        :return: bool
        """
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    class Meta:
        abstract = True
