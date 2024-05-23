from django.urls import path
from .views import ChatRoomView, MessagesView, ChatRoomMembersView, SameChatRoomAPI, LeaveChatRoomAPI, \
	CreateUserSeenMessagesAPI, ListUserSeenMessagesAPI

urlpatterns = [
	path('chats/', ChatRoomView.as_view(), name='chatRoom'),
	path('chats/<str:room_id>/messages', MessagesView.as_view(), name='message_list'),
	path('chats/<str:room_id>/messages/seen', CreateUserSeenMessagesAPI.as_view(),
		 name='seen_message'),
	path('chats/<str:room_id>/messages/<int:message_id>/seen', ListUserSeenMessagesAPI.as_view(),
		 name='seen_message_list_users'),
	path('chats/<str:room_id>/leave', LeaveChatRoomAPI.as_view(), name='chat_room_leave'),
	path('chats/<str:room_id>/members', ChatRoomMembersView.as_view(), name='membersList'),
	path('users/<int:user_id>/chats', SameChatRoomAPI.as_view(), name='same_chat_rooms_list'),
]
