from django.urls import path
from .views import ChatRoomView, MessagesView, ChatRoomMembersView, SameChatRoomAPI, LeaveChatRoomAPI

urlpatterns = [
	path('chats/', ChatRoomView.as_view(), name='chatRoom'),
	path('chats/<str:room_id>/messages', MessagesView.as_view(), name='messageList'),
	path('chats/<str:room_id>/leave', LeaveChatRoomAPI.as_view(), name='chat_room_leave'),
	path('chats/<str:room_id>/members', ChatRoomMembersView.as_view(), name='membersList'),
	path('users/<int:user_id>/chats', SameChatRoomAPI.as_view(), name='same_chat_rooms_list'),
]
