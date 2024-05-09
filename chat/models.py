from django.db import models
from users.models import CustomerUser
from shortuuidfield import ShortUUIDField


# Create your models here.

class ChatRoom(models.Model):
    CHAT_ROOM_CHOICES = (
        ('direct', 'Direct Chat'),
        ('group', 'Group')
    )
    room_id = ShortUUIDField()
    type = models.CharField(max_length=10, default='direct', choices=CHAT_ROOM_CHOICES)
    member = models.ManyToManyField(CustomerUser, related_name='members', blank=True)
    post = models.ForeignKey('post.Post', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    admin = models.ManyToManyField(CustomerUser, related_name='admins', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_id + ' -> ' + str(self.name)


class ChatMessage(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, related_name='messages',)
    user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=255)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey('post.Post', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_by = models.ManyToManyField(CustomerUser, related_name='deleted_by', blank=True)

    def __str__(self):
        return self.message
