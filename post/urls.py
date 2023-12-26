from django.urls import path

from post.views import ListCreateUserPostAPI

urlpatterns = [
    path('me/post', ListCreateUserPostAPI.as_view(), name='user_post_create_list')
]