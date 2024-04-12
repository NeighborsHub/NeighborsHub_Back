from django.contrib import admin
from .models import CustomerUser, OnlineUser

admin.site.register(CustomerUser)
admin.site.register(OnlineUser)
