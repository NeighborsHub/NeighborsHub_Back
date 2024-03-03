from django.shortcuts import render
from rest_framework import generics

from NeighborsHub.custom_view_mixin import ExpressiveListModelMixin, ExpressiveCreateModelMixin
from NeighborsHub.permission import CustomAuthentication, CustomAuthenticationWithoutEffect
from albums.models import Media, UserAvatar
from albums.serializers import MyListMediaSerializer, UserListMediaSerializer, UserAvatarSerializer


class MyListGalleryAPI(ExpressiveListModelMixin, generics.ListAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = MyListMediaSerializer
    plural_name = 'medias'

    def get_queryset(self):
        return Media.objects.filter(created_by=self.request.user).prefetch_related('post')


class UserListGalleryAPI(ExpressiveListModelMixin, generics.ListAPIView):
    authentication_classes = (CustomAuthenticationWithoutEffect,)
    serializer_class = UserListMediaSerializer
    plural_name = 'medias'

    def get_queryset(self):
        media = Media.objects.filter(created_by_id=self.kwargs['user_pk']).select_related('created_by')
        media = media.prefetch_related('post')
        return media


class MyListAvatarsAPI(ExpressiveListModelMixin, ExpressiveCreateModelMixin, generics.ListCreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = UserAvatarSerializer
    plural_name = 'avatars'
    singular_name = 'avatar'

    def get_queryset(self):
        return UserAvatar.objects.filter(user=self.request.user, created_by=self.request.user)


class UserListAvatarsAPI(ExpressiveListModelMixin, generics.ListAPIView):
    serializer_class = UserAvatarSerializer
    plural_name = 'avatars'

    def get_queryset(self):
        return UserAvatar.objects.filter(user=self.kwargs['user_pk'], created_by=self.kwargs['user_pk'])
