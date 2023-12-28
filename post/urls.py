from django.urls import path

from post.views import CreateUserPostAPI, ListUserPostAPI, RetrieveUpdateDeleteUserPostAPI

urlpatterns = [
    path('me/create', CreateUserPostAPI.as_view(), name='user_post_create'),
    path('me', ListUserPostAPI.as_view(), name='user_post_list'),
    path('me/<int:pk>', RetrieveUpdateDeleteUserPostAPI.as_view(), name='user_post_update_retrieve_delete'),
]