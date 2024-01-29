import datetime
import re
from uuid import uuid4

from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager

from NeighborsHub.exceptions import NotOwnAddressException
from core.models import BaseModel, City, States, Hashtag


def validate_email(value: str) -> bool:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, value) is not None


def validate_mobile(value: str) -> bool:
    mobile_regex = r"^[0-9]{7,}$"
    return re.match(mobile_regex, value) is not None


class CustomUserManager(UserManager):
    def _create_user(self, mobile, email, password, **extra_fields):
        user = self.model(mobile=mobile, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(mobile, email, password, **extra_fields)

    def create_superuser(self, mobile, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(mobile, email, password, **extra_fields)

    def get_user_with_mobile_or_mail(self, user_field):
        return self.get(Q(email=user_field) | Q(mobile=user_field))


class CustomerUser(AbstractBaseUser, PermissionsMixin):
    is_staff = models.BooleanField(default=False)  # a admin user; non super-user
    is_superuser = models.BooleanField(default=False)  # a superus
    email = models.EmailField(unique=True, blank=True, null=True, max_length=100)
    username = models.CharField(max_length=50, unique=True)
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True, validators=[validate_mobile])
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified_mobile = models.BooleanField(default=False)
    is_verified_email = models.BooleanField(default=False)
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='customUser_set',
        related_query_name='user'
    )
    groups = models.ManyToManyField(Group, related_name='customer_users')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile', ]
    state = models.ForeignKey(States, null=True, blank=True, on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    hashtags = models.ManyToManyField(Hashtag, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_email_at = models.DateTimeField(blank=True, null=True)
    verified_mobile_at = models.DateTimeField(blank=True, null=True)
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.username = uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Follow(BaseModel):
    follower = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT, related_name='follower')
    following = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT,
                                  related_name='following')

    def __str__(self):
        return (
            f"Follow(id={self.id}, status={self.state}, following_user_id={self.follower.id}, followed_user_id={self.following.id}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})")


class Address(BaseModel):
    user = models.ForeignKey(CustomerUser, null=True, blank=True, on_delete=models.PROTECT, unique=False)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    is_main_address = models.BooleanField(default=False, null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    is_public = models.BooleanField(default=True)

    def is_user_owner(self, user, raise_exception=False):
        is_owner = self.user == user
        if raise_exception and not is_owner:
            raise NotOwnAddressException
        return is_owner

    def save(self, *args, **kwargs):
        if self.is_main_address:
            Address.objects.filter(user=self.user).update(is_main_address=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Address(id={self.id}, status={self.state}, user_id={self.user.id},  "
                f"created_at={self.created_at}, updated_at={self.updated_at})")
