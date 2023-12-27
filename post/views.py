from rest_framework import generics, serializers
from rest_framework.parsers import FormParser, MultiPartParser

from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin
from NeighborsHub.exceptions import NotOwnAddressException
from NeighborsHub.permission import CustomAuthentication
from post.models import Post
from post.serializers import CreatePostSerializer
from users.models import Address


class CreateUserPostAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = CreatePostSerializer
    queryset = Post.objects.all()
    singular_name = 'post'

    def perform_create(self, serializer):
        address = Address.objects.filter(id=serializer.validated_data['address_id']).first()
        if address is None or not address.is_user_owner(self.request.user, raise_exception=True):
            raise NotOwnAddressException
        address = serializer.save(user=self.request.user)
        return address

