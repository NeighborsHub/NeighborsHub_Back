from rest_framework import generics

from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin
from NeighborsHub.permission import CustomAuthentication
from post.models import Post
from post.serializers import CreatePostSerializer


class CreateUserPostAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = CreatePostSerializer
    queryset = Post.objects.all()
    singular_name = 'post'

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user, address_id=serializer.validated_data['address_id'])
        return address

