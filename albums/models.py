from django.db import models
from users.models import CustomerUser
from core.models import BaseModel


# Create your models here.

class Media(BaseModel):
    file = models.FileField(upload_to='media/')

    def __str__(self):
        return self.file.name


class UserAvatar(BaseModel):
    avatar = models.ForeignKey(Media, null=True, blank=True, on_delete=models.PROTECT)
    user = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT)
