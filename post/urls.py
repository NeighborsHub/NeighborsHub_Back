from django.urls import path

from post.views import CreateUserPostAPI

urlpatterns = [
    path('create', CreateUserPostAPI.as_view(), name='user_post_create')
]