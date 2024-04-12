from django.db import models
from users.models import CustomerUser
from shortuuidfield import ShortUUIDField


# Create your models here.

class ChatRoom(models.Model):
    roomId = ShortUUIDField()
    type = models.CharField(max_length=10, default='DM')
    member = models.ManyToManyField(CustomerUser)
    name = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.roomId + ' -> ' + str(self.name)


class ChatMessage(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
