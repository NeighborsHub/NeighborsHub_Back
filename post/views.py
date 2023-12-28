from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser

from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin, \
    ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin
from NeighborsHub.exceptions import NotOwnAddressException, ObjectNotFoundException
from NeighborsHub.permission import CustomAuthentication, IsOwnerAuthentication
from post.models import Post
from post.serializers import PostSerializer, MyListPostSerializer
from users.models import Address


class CreateUserPostAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    singular_name = 'post'

    def perform_create(self, serializer):
        address = Address.objects.filter(id=serializer.validated_data['address_id']).first()
        if address is None or not address.is_user_owner(self.request.user, raise_exception=True):
            raise NotOwnAddressException
        address = serializer.save(user=self.request.user)
        return address


class ListUserPostAPI(ExpressiveListModelMixin, generics.ListAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = MyListPostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    queryset = Post.objects.all()
    filterset_fields = ['address_id', ]
    search_fields = ['title', 'body']

    plural_name = 'posts'

    def get_queryset(self):
        return Post.objects.f


class RetrieveUpdateDeleteUserPostAPI(ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin,
                                generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (CustomAuthentication,)
    permission_classes = (IsOwnerAuthentication,)
    serializer_class = PostSerializer
    singular_name = 'post'
    queryset = Post.objects.all()

    def get_object(self):
        try:
            obj = Post.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
        except Post.DoesNotExist:
            raise ObjectNotFoundException
        return obj
