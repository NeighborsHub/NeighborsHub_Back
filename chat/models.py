from django.db import models
from users.models import CustomerUser
from core.models import BaseModel

# Create your models here.

class Chat(BaseModel):
    users = models.ManyToManyField(CustomerUser, related_name='chats_users')
    finished_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True,blank=True)
    def __str__(self):
        return (f"Chat(id={self.id}")


class Message(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    body = models.TextField()

    def __str__(self):
        return (f"Message(id={self.id}, chat={self.chat}, body={self.body}, "
                f"created_at={self.created_at}, created_by={self.created_by})")


class MessageSeen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.PROTECT)
    users = models.ManyToManyField(CustomerUser, related_name='messages_seen_users')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MessageSeen(id={self.id}, message={self.message}, created_at={self.created_at})"
