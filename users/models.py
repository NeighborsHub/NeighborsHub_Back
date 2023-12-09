from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission

from core.models import BaseModel, City, States, Hashtag


class CustomerUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=30, unique=True)
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='customuser_set',
        related_query_name='user'
    )
    groups = models.ManyToManyField(Group, related_name='customer_users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    state = models.ForeignKey(States, null=True, blank=True, on_delete=models.PROTECT)
    hashtags = models.ManyToManyField(Hashtag, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Follow(BaseModel):
    follower = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT)
    following = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return (f"Follow(id={self.id}, status={self.state}, following_user_id={self.follower.id}, followed_user_id={self.following.id}, "
                f"created_at={self.created_at}, updated_at={self.updated_at})")


class Address(BaseModel):
    user = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    is_main_address = models.BooleanField(default=False)
    def __str__(self):
        return (f"Address(id={self.id}, status={self.state}, user_id={self.user.id},  "
                f"created_at={self.created_at}, updated_at={self.updated_at})")

