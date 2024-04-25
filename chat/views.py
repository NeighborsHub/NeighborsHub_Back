from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.pagination import LimitOffsetPagination

from NeighborsHub.custom_view_mixin import ExpressiveListModelMixin, ExpressiveUpdateModelMixin
from NeighborsHub.exceptions import YouAreNotGroupAdminException
from NeighborsHub.permission import CustomAuthentication
from users.models import CustomerUser
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatRoomMembersSerializer, \
    RemoveChatMessageSerializer, LeaveChatRoomSerializer
from .models import ChatRoom, ChatMessage
from django.utils.translation import gettext as _


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
    plural_name = "chat_room_members"

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return ChatRoom.objects.get(room_id=room_id).member.all()

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
    authentication_classes = (CustomAuthentication,)
    serializer_class = ChatMessageSerializer
    pagination_class = LimitOffsetPagination
    plural_name = 'chat_messages'

    def get_queryset(self):
        chats = ChatMessage.objects.filter(chat__room_id=self.kwargs['room_id'])
        chats = chats.exclude(deleted_by=self.request.user).order_by('-created_at')
        return chats


class SameChatRoomAPI(ExpressiveListModelMixin, ListAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = ChatRoomSerializer
    plural_name = 'chat_rooms'

    def get_queryset(self):
        chats = ChatRoom.objects.filter(member=self.request.user)
        chats = chats.filter(member=CustomerUser.objects.get(id=self.kwargs['user_id']))
        chats = chats.order_by('type', '-created_at')
        return chats


class LeaveChatRoomAPI(DestroyAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = LeaveChatRoomSerializer
    plural_name = 'chat_rooms'

    def get_object(self):
        return ChatRoom.objects.get(room_id=self.kwargs['room_id'])

    def delete_my_message_for_all(self, chatroom):
        return ChatMessage.objects.filter(chat=chatroom, user=self.request.user).delete()

    def delete_all_message_for_me(self, chatroom):
        chat_messages = ChatMessage.objects.filter(chat=chatroom)
        for chat_message in chat_messages:
            chat_message.deleted_by.add(self.request.user)
        return

    def perform_destroy(self, instance):
        instance.member.remove(self.request.user)

        serializer = LeaveChatRoomSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.validated_data['delete_my_messages_for_all']:
            self.delete_my_message_for_all(instance)

        if serializer.validated_data['delete_all_message_for_me']:
            self.delete_all_message_for_me(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteChatMessagesAPI(DestroyAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = RemoveChatMessageSerializer
    plural_name = 'chat_messages'

    def get_object(self):
        return ChatRoom.objects.get(room_id=self.kwargs['room_id'])

    def delete_my_message_for_all(self, chatroom, message_ids):
        return ChatMessage.objects.filter(chat=chatroom, id__in=[m['id'] for m in message_ids],
                                          user=self.request.user).delete()

    def delete_all_message_for_me(self, chatroom, message_ids):
        chat_messages = ChatMessage.objects.filter(chat=chatroom, id__in=[m['id'] for m in message_ids])
        for chat_message in chat_messages:
            chat_message.deleted_by.add(self.request.user)
        return

    def perform_destroy(self, instance):
        serializer = RemoveChatMessageSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.validated_data['delete_my_messages_for_all']:
            self.delete_my_message_for_all(instance, serializer.validated_data['message_ids'])

        if serializer.validated_data['delete_all_message_for_me']:
            self.delete_all_message_for_me(instance, serializer.validated_data['message_ids'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"status": "ok", 'data': {}, 'message': _('Messages deleted successfully.')},
                        status=status.HTTP_204_NO_CONTENT)
