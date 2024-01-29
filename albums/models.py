from django.db import models
from core.models import BaseModel
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Media(BaseModel):
    file = models.FileField(upload_to='media/')

    def __str__(self):
        return self.file.name


class UserAvatar(BaseModel):
    avatar = models.ImageField(upload_to='media/avatar/')
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(300, 300)],
                                      format='JPEG',
                                      options={'quality': 60})
    user = models.ForeignKey('users.CustomerUser', null=True, blank=True, on_delete=models.PROTECT,
                             related_name='avatar')

    def __str__(self):
        return f"UserAvatar(user_id: {self.user_id} - filename:{self.avatar.file.name})"
