from django.urls import path

from users.views import RegisterAPI

urlpatterns = [
    path('/register', RegisterAPI.as_view(), name='user_register')
]
