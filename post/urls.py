from django.urls import path

from post.views import CreateUserPostAPI, ListUserPostAPI, RetrieveUpdateDeleteUserPostAPI, ListPostAPI, \
    CreateCommentAPI

urlpatterns = [
    path('me/create', CreateUserPostAPI.as_view(), name='user_post_create'),
    path('me', ListUserPostAPI.as_view(), name='user_post_list'),
    path('me/<int:pk>', RetrieveUpdateDeleteUserPostAPI.as_view(), name='user_post_update_retrieve_delete'),
    path('', ListPostAPI.as_view(), name='post_list'),
    path('<int:pk>/comment', CreateCommentAPI.as_view(), name='create_post_comment'),
]