import re

from django.db import models

from albums.models import Media
from core.models import BaseModel, Hashtag


# Create your models here.


class Post(BaseModel):
    title = models.CharField(max_length=255)
    body = models.TextField()
    media = models.ManyToManyField(Media, null=True, blank=True)

    def extract_hashtags(self):
        hashtags = re.findall(r'#(\w+)', self.body)
        return hashtags

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        hashtags = self.extract_hashtags()
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(hashtag_title=tag.lower())
            self.hashtags.add(hashtag)

    def __str__(self):
        return (f"Post(id={self.id}, title={self.title}, state={self.state},"
                f" created_at={self.created_at}, updated_at={self.updated_at},"
                f" created_by={self.created_by}, updated_by={self.updated_by})")


class Comment(BaseModel):
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    reply_to = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return (f"Comment(id={self.id}, body={self.body}, state={self.state},"
                f" post={self.post}, reply_to={self.reply_to}, hashtags={self.hashtags},"
                f" created_at={self.created_at}, updated_at={self.updated_at},"
                f" created_by={self.created_by}, updated_by={self.updated_by})")


class Like(BaseModel):
    LIKE_CHOICES = (
        ('support', 'Support'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        # Add more choices as needed
    )
    type = models.CharField(max_length=10, choices=LIKE_CHOICES)

    def __str__(self):
        return (f"Like(id={self.id}",
                f" type={self.type}, created_at={self.created_at})")


class LikePost(Like):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_likes')


class LikeComment(Like):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_likes')
