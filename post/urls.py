from django.urls import path

from post.views import CreateUserPostAPI, ListUserPostAPI

urlpatterns = [
    path('me/create', CreateUserPostAPI.as_view(), name='user_post_create'),
    path('me', ListUserPostAPI.as_view(), name='user_post_list')
]