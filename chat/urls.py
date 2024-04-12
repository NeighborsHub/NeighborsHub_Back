from django.urls import path
from .views import ChatRoomView, MessagesView

urlpatterns = [
	path('chats', ChatRoomView.as_view(), name='chatRoom'),
	path('chats/<str:room_id>/messages', MessagesView.as_view(), name='messageList'),
	path('users/<int:user_id>/chats', ChatRoomView.as_view(), name='chatRoomList'),
]
