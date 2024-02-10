import os
from io import BytesIO

import requests
from django.core.files import File
from django.db import models
from django.conf import settings

from core.models import BaseModel
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.utils.text import get_valid_filename

from users.models import CustomerUser

from django.core.files.storage import FileSystemStorage


class UserFileSystemStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # Generate a unique filename
        while self.exists(name):
            name = self.get_valid_name(name)
        return name

    @staticmethod
    def get_user_upload_path(obj: any, filename: str) -> str:
        return os.path.join(f'{obj.created_by.unique_id}', get_valid_filename(filename))


user_upload_storage = UserFileSystemStorage()


class Media(BaseModel):
    file = models.FileField(upload_to=user_upload_storage.get_user_upload_path)

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

    @staticmethod
    def save_from_url(image_url, user):
        response = requests.get(image_url)
        if response.status_code == 200:
            obj = UserAvatar()
            image_io = BytesIO(response.content)
            obj.avatar.save(image_url.split('/')[-1], File(image_io))
            obj.user = user
            obj.created_by = user
            obj.updated_by = user
            obj.save()
