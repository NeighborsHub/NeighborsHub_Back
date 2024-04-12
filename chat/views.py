from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from .models import ChatRoom, ChatMessage


class ChatRoomView(APIView):
    @staticmethod
    def get(request, user_id):
        chat_rooms = ChatRoom.objects.filter(member=user_id)
        serializer = ChatRoomSerializer(
            chat_rooms, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        serializer = ChatRoomSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessagesView(ListAPIView):
    serializer_class = ChatMessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        room_id = self.kwargs['roomId']
        return ChatMessage.objects.filter(chat__roomId=room_id).order_by('-created_at')
