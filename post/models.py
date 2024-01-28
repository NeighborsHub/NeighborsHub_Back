import re

from django.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance


from albums.models import Media
from core.models import BaseModel, Hashtag
from users.models import Address


class PostManager(models.Manager):
    def filter_post_distance_of_location(self, location_point: Point, distance):
        return self.annotate(distance=GeometryDistance('address__location', location_point)).filter(distance__lt=distance)


class Post(BaseModel):
    hashtags = models.ManyToManyField(Hashtag, blank=True, through='PostHashtag')
    title = models.CharField(max_length=255)
    body = models.TextField()
    media = models.ManyToManyField(Media, null=True, blank=True)
    address = models.ForeignKey(Address, null=True, blank=True,
                                related_name='post_address', on_delete=models.CASCADE)

    objects = PostManager()

    def extract_hashtags(self):
        hashtags = re.findall(r'#(\w+)', self.body)
        return hashtags

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        hashtags = [hashtag.lower() for hashtag in self.extract_hashtags()]
        self.posthashtag_set.exclude(hashtag__hashtag_title__in=hashtags).delete()
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(hashtag_title=tag)
            self.hashtags.add(hashtag)

    def __str__(self):
        return (f"Post(id={self.id}, title={self.title}, state={self.state},"
                f" created_at={self.created_at}, updated_at={self.updated_at},"
                f" created_by={self.created_by}, updated_by={self.updated_by})")


class Comment(BaseModel):
    body = models.TextField()
    hashtags = models.ManyToManyField(Hashtag, blank=True, through='CommentHashtag')

    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING, related_name='comment_post')
    reply_to = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True)

    def extract_hashtags(self):
        hashtags = re.findall(r'#(\w+)', self.body)
        return hashtags

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        hashtags = [hashtag.lower() for hashtag in self.extract_hashtags()]
        self.commenthashtag_set.exclude(hashtag__hashtag_title__in=hashtags).delete()
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(hashtag_title=tag)
            self.hashtags.add(hashtag)

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
        return f"Like(id={self.id}, type={self.type}, created_at={self.created_at})"

    class Meta:
        abstract = True


class LikePost(Like):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_likes')


class LikeComment(Like):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_likes')


class PostHashtag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PostHashtag(post={self.post_id} , title={self.hashtag.hashtag_title}, created_at={self.created_at})"


class CommentHashtag(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CommentHashtag(post={self.comment} , title={self.hashtag.hashtag_title}, created_at={self.created_at})"
