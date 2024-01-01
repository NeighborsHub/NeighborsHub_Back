from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter

from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin, \
    ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin
from NeighborsHub.exceptions import NotOwnAddressException, ObjectNotFoundException
from NeighborsHub.permission import CustomAuthentication, IsOwnerAuthentication
from post.filters import ListPostFilter
from post.models import Post, Comment
from post.serializers import PostSerializer, MyListPostSerializer, CommentSerializer, ListCommentSerializer
from users.models import Address
from django.contrib.gis.geos import Point


class CreateUserPostAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    singular_name = 'post'

    def perform_create(self, serializer):
        address = Address.objects.filter(id=serializer.validated_data['address_id']).first()
        if address is None or not address.is_user_owner(self.request.user, raise_exception=True):
            raise NotOwnAddressException
        post = serializer.save(user=self.request.user)
        return post


class ListUserPostAPI(ExpressiveListModelMixin, generics.ListAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = MyListPostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    queryset = Post.objects.all()
    filterset_fields = ['address_id', ]
    search_fields = ['title', 'body']

    plural_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(created_by=self.request.user)


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


class ListPostAPI(ExpressiveListModelMixin, generics.ListAPIView):
    serializer_class = MyListPostSerializer
    queryset = Post.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ListPostFilter
    plural_name = 'posts'

    def get_queryset(self):
        if (self.request.query_params.get('latitude') is not None and
                self.request.query_params.get('longitude') is not None):
            user_location = Point(float(self.request.query_params.get('longitude')),
                                  float(self.request.query_params.get('latitude')),
                                  srid=4326)
            return Post.objects.filter_post_distance_of_location(user_location,
                                                                 distance=int(
                                                                     self.request.query_params.get('distance')))
        return Post.objects.all()


class CreateCommentAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    singular_name = 'comment'

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['post_pk'])
        comment = serializer.save(user=self.request.user, post=post)
        return comment


class RetrieveUpdateDeleteCommentAPI(ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin,
                                     generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (CustomAuthentication,)
    permission_classes = (IsOwnerAuthentication,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    singular_name = 'comment'

    def get_object(self):
        try:
            obj = Comment.objects.get(post_id=self.kwargs['post_pk'], id=self.kwargs['comment_pk'])
            self.check_object_permissions(self.request, obj)
        except Comment.DoesNotExist:
            raise ObjectNotFoundException
        return obj


class ListCommentAPI(ExpressiveListModelMixin, generics.ListAPIView):
    serializer_class = ListCommentSerializer
    plural_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'], reply_to__isnull=True).order_by('-id')
