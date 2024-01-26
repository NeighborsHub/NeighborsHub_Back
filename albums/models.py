from django.db import models
from core.models import BaseModel


class Media(BaseModel):
    file = models.FileField(upload_to='media/')

    def __str__(self):
        return self.file.name


class UserAvatar(BaseModel):
    avatar = models.ForeignKey(Media, null=True, blank=True, on_delete=models.PROTECT)
    user = models.ForeignKey('users.CustomerUser', null=True, blank=True, on_delete=models.PROTECT, related_name='avatar')

    def __str__(self):
        return f"UserAvatar(user_id: {self.user_id} - filename:{self.avatar.file.name})"

