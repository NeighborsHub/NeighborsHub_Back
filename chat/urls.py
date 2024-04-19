from django.urls import path
from .views import ChatRoomView, MessagesView, ChatRoomMembersView

urlpatterns = [
	path('chats/', ChatRoomView.as_view(), name='chatRoom'),
	path('chats/<str:room_id>/messages', MessagesView.as_view(), name='messageList'),
	path('chats/<str:room_id>/members', ChatRoomMembersView.as_view(), name='membersList'),
	path('users/<int:user_id>/chats', ChatRoomView.as_view(), name='chatRoomList'),
]
