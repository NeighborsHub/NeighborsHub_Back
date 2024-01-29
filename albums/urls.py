from django.urls import path

from albums.views import MyListGalleryAPI, UserListGalleryAPI, MyListAvatarsAPI, UserListAvatarsAPI

urlpatterns = [
    path('media/me', MyListGalleryAPI.as_view(), name='media_mylist'),
    path('media/user/<int:user_pk>', UserListGalleryAPI.as_view(), name='media_user_list'),
    path('avatar/me', MyListAvatarsAPI.as_view(), name='avatar_mylist'),
    path('avatar/user/<int:user_pk>', UserListAvatarsAPI.as_view(), name='avatar_user_list'),

]
