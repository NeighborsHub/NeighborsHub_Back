from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.pagination import LimitOffsetPagination

from NeighborsHub.custom_view_mixin import ExpressiveListModelMixin, ExpressiveUpdateModelMixin
from NeighborsHub.exceptions import YouAreNotGroupAdminException
from NeighborsHub.permission import CustomAuthentication
from users.models import CustomerUser
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatRoomMembersSerializer
from .models import ChatRoom, ChatMessage


class ChatRoomView(APIView):
    authentication_classes = (CustomAuthentication,)

    def get(self, request):
        chat_rooms = ChatRoom.objects.filter(member=self.request.user)
        serializer = ChatRoomSerializer(
            chat_rooms, many=True, context={"request": request}
        )
        return Response({"status": "ok", "data": serializer.data, "message": ""},
                        status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ChatRoomSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ok", "data": serializer.data, "message": "ChatRoom Created"},
                            status=status.HTTP_201_CREATED)
        return Response({"status": "error", 'data': serializer.errors, 'message': 'Inputs has errors'}
                        , status=status.HTTP_400_BAD_REQUEST)


class ChatRoomMembersView(ExpressiveListModelMixin, ExpressiveUpdateModelMixin, ListAPIView, UpdateAPIView):
    authentication_classes = (CustomAuthentication,)
    pagination_class = LimitOffsetPagination
    serializer_class = ChatRoomMembersSerializer
    singular_name = "chat_room_members"

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return ChatRoom.objects.get(room_id=room_id)

    def get_object(self):
        room_id = self.kwargs['room_id']
        return ChatRoom.objects.get(room_id=room_id)

    def perform_update(self, serializer):
        if not serializer.is_valid():
            return Response({"status": "error", 'data': serializer.errors, 'message': 'Inputs has errors'}
                            , status=status.HTTP_400_BAD_REQUEST)
        obj = self.get_queryset()
        if self.request.user not in obj.admin.all() and \
                (len(serializer.validated_data['admins']) > 0 or len(serializer.validated_data['delete_admins']) > 0):
            raise YouAreNotGroupAdminException()
        serializer.save()


class MessagesView(ExpressiveListModelMixin, ListAPIView):
    serializer_class = ChatMessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return ChatMessage.objects.filter(chat__room_id=room_id).order_by('-created_at')
