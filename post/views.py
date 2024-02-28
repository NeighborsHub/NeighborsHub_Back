from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.filters import InBBoxFilter
from django.contrib.gis.geos import Polygon

from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin, \
    ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin
from NeighborsHub.exceptions import NotOwnAddressException, ObjectNotFoundException
from NeighborsHub.permission import CustomAuthentication, IsOwnerAuthentication, CustomAuthenticationWithoutEffect
from post.filters import ListPostFilter
from post.models import Post, Comment, LikePost, LikeComment
from post.serializers import PostSerializer, MyListPostSerializer, CommentSerializer, ListCommentSerializer, \
    LikePostSerializer, LikeCommentSerializer, ListCountLocationPostsSerializer, PublicListPostSerializer
from post.models import Post, Comment
from post.serializers import PostSerializer, MyListPostSerializer, CommentSerializer, ListCommentSerializer, \
    RetrievePostSerializer
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


class RetrievePost(ExpressiveRetrieveModelMixin, generics.RetrieveAPIView):
    authentication_classes = (CustomAuthenticationWithoutEffect,)
    permission_classes = (IsOwnerAuthentication,)
    serializer_class = RetrievePostSerializer
    singular_name = 'post'
    queryset = Post.objects.all()

    def get_object(self):
        try:
            obj = Post.objects.get(pk=self.kwargs['post_pk'])
        except Post.DoesNotExist:
            raise ObjectNotFoundException
        return obj


class ListPostAPI(ExpressiveListModelMixin, generics.ListAPIView):
    authentication_classes = (CustomAuthenticationWithoutEffect,)
    serializer_class = PublicListPostSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, SearchFilter]
    filterset_class = ListPostFilter
    plural_name = 'posts'
    bbox_filter_field = 'address__location'

    def get_user_location_point(self):
        if (self.request.query_params.get('user_latitude') is not None and
                self.request.query_params.get('user_longitude') is not None):
            return Point(float(self.request.query_params.get('user_longitude')),
                         float(self.request.query_params.get('user_latitude')),
                         srid=4326)

    def get_post_location_point(self):
        if (self.request.query_params.get('post_latitude') is not None and
                self.request.query_params.get('post_longitude') is not None):
            return Point(float(self.request.query_params.get('post_longitude')),
                         float(self.request.query_params.get('post_latitude')),
                         srid=4326)

    def get_queryset(self):
        posts = Post.objects.filter_posts_location_user_distance(
            user_location=self.get_user_location_point(),
            post_location=self.get_post_location_point(),
            from_distance=self.request.query_params.get('from_distance', None),
            to_distance=self.request.query_params.get('to_distance', None)
        )
        posts = posts.exclude(created_by=self.request.user) if self.request.user is not None else posts
        return posts


class ListCountLocationPostAPI(ExpressiveListModelMixin, generics.ListAPIView):
    authentication_classes = (CustomAuthenticationWithoutEffect,)
    serializer_class = ListCountLocationPostsSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, SearchFilter]
    filterset_class = ListPostFilter
    plural_name = 'posts'
    bbox_filter_field = 'address__location'

    def get_user_near_post(self):
        if (self.request.query_params.get('user_latitude') is not None and
                self.request.query_params.get('user_longitude') is not None):
            user_location = Point(float(self.request.query_params.get('user_longitude')),
                                  float(self.request.query_params.get('user_latitude')),
                                  srid=4326)
            return Post.objects.filter_post_distance_of_location(
                user_location,
                from_distance=self.request.query_params.get('from_distance', None),
                to_distance=self.request.query_params.get('to_distance', None)
            )
        return Post.objects.all()

    def get_queryset(self):
        posts = self.get_user_near_post()
        posts = posts.exclude(created_by=self.request.user) if self.request.user is not None else posts
        posts = posts.values('address__location').annotate(posts_count=Count('address__location'))
        return posts


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
    authentication_classes = (CustomAuthenticationWithoutEffect,)
    serializer_class = ListCommentSerializer
    plural_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'], reply_to__isnull=True).order_by('-id')


class LikePostAPI(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def post(request, post_pk):
        serializer = LikePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        LikePost.objects.filter(post_id=post_pk, created_by=request.user).delete()
        like_post = LikePost.objects.create(
            created_by=request.user, updated_by=request.user,
            post_id=post_pk, type=serializer.validated_data['type']
        )
        like_post.save()
        return Response(data={"status": "ok", "data": {}, "message": "Like post successfully"})

    @staticmethod
    def delete(request, post_pk):
        LikePost.objects.filter(created_by=request.user, post_id=post_pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeCommentAPI(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def post(request, comment_pk):
        serializer = LikeCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        LikeComment.objects.filter(comment_id=comment_pk, created_by=request.user).delete()
        like_comment = LikeComment.objects.create(
            created_by=request.user, updated_by=request.user,
            comment_id=comment_pk, type=serializer.validated_data['type']
        )
        like_comment.save()
        return Response(data={"status": "ok", "data": {}, "message": "Like comment successfully"})

    @staticmethod
    def delete(request, comment_pk):
        LikeComment.objects.filter(created_by=request.user, comment_id=comment_pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
