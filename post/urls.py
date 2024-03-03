from django.urls import path

from post.views import CreateUserPostAPI, ListUserPostAPI, RetrieveUpdateDeleteUserPostAPI, ListPostAPI, \
    CreateCommentAPI, RetrieveUpdateDeleteCommentAPI, ListCommentAPI, RetrievePost, LikePostAPI, LikeCommentAPI, \
    ListCountLocationPostAPI, ListCategoryAPI, ListPublicUserPostAPI

urlpatterns = [
    path('me/post/create', CreateUserPostAPI.as_view(), name='user_post_create'),
    path('me/post/', ListUserPostAPI.as_view(), name='user_post_list'),
    path('me/post/<int:pk>', RetrieveUpdateDeleteUserPostAPI.as_view(), name='user_post_update_retrieve_delete'),
    path('user/<int:user_pk>/post/', ListPublicUserPostAPI.as_view(), name='public_user_post_list'),
    path('post/', ListPostAPI.as_view(), name='post_list'),
    path('post/location-count', ListCountLocationPostAPI.as_view(), name='post_location_count'),
    path('post/<int:post_pk>/comment', CreateCommentAPI.as_view(), name='create_post_comment'),
    path('post/<int:post_pk>', RetrievePost.as_view(), name='post_retrieve'),
    path('post/<int:post_pk>/comments', ListCommentAPI.as_view(), name='list_post_comment'),
    path('post/<int:post_pk>/comment/<int:comment_pk>', RetrieveUpdateDeleteCommentAPI.as_view(),
         name='post_comment_update_delete'),
    path('post/<int:post_pk>/like', LikePostAPI.as_view(), name='post_like'),
    path('post/comment/<int:comment_pk>/like', LikeCommentAPI.as_view(), name='comment_like'),

    path('post/category/', ListCategoryAPI.as_view(), name='list_category')
]