from django.test import TestCase
from model_bakery import baker
from rest_framework import status

from NeighborsHub.test_function import test_object_attributes_existence
from chat.models import ChatRoom, ChatMessage
from users.models import CustomerUser
from users.tests import _create_user
from rest_framework.test import APIClient
from rest_framework.reverse import reverse


class TsetChatRoomModel(TestCase):

    def test_property_type_model_exists(self):
        a = ChatRoom()
        self.assertTrue(isinstance(a, ChatRoom))

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'type', 'room_id', 'created_at', 'member', 'name', 'admin'
        ]
        chat_room = ChatRoom
        test_object_attributes_existence(self, chat_room, attributes)

    def test_user_model(self):
        created_obj = baker.make(ChatRoom)
        test_obj = ChatRoom.objects.filter(id=created_obj.id).first()
        self.assertIsNotNone(test_obj)


class TsetChatMessageModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        ChatMessage()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'chat_id', 'message', 'user_id', 'post_id', 'reply_to_id',
            'updated_at', 'deleted_by', 'created_at'
        ]
        chat_message = ChatMessage
        test_object_attributes_existence(self, chat_message, attributes)

    def test_successfully_create(self):
        created_obj = baker.make(ChatMessage)
        test_obj = ChatMessage.objects.filter(id=created_obj.id).first()
        self.assertIsNotNone(test_obj)


class TestCreateDirectMessage(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.post(reverse('chatRoom'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_direct_chatroom(self):
        self.client.force_authenticate(self.user)
        tmp_user = baker.make(CustomerUser)
        tmp_user_2 = baker.make(CustomerUser)
        data = {
            'type': 'direct',
            'members': [{'id': tmp_user.id}],
            'name': 'Test Direct'
        }
        response = self.client.post(reverse('chatRoom'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('chatRoom'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('error', response_json['status'])
        self.assertIn('members', response_json['data'])

    def test_create_group_chatroom(self):
        self.client.force_authenticate(self.user)
        tmp_user = baker.make(CustomerUser)
        tmp_user_2 = baker.make(CustomerUser)
        data = {
            'type': 'group',
            'members': [{'id': tmp_user.id}, {'id': tmp_user_2.id}],
            'name': 'Test Direct'
        }
        response = self.client.post(reverse('chatRoom'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('member', response_json['data'])
        self.assertEqual(3, len(response_json['data']['member']))
        self.assertIn('type', response_json['data'])
        self.assertIn('room_id', response_json['data'])
        self.assertIn('admin', response_json['data'])
        self.assertIn('admin', response_json['data'])
        self.assertEqual(1, len(response_json['data']['admin']))


class TestChatRoomMemberListMessage(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_user = baker.make(CustomerUser)
        self.chat_room = baker.make(ChatRoom, type='group')
        self.chat_room.member.set([self.tmp_user, self.user])
        self.chat_room.admin.set([self.user, self.tmp_user])

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('membersList', kwargs={'room_id': self.chat_room.room_id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_updates_anonymous_user(self):
        anonymous_user = baker.make(CustomerUser)
        self.client.force_authenticate(anonymous_user)
        data = {
            'admins': [{'id': anonymous_user.id}]
        }
        response = self.client.put(reverse('membersList', kwargs={'room_id': self.chat_room.room_id}),
                                   data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_group_chatroom(self):
        self.client.force_authenticate(self.user)
        anonymous = baker.make(CustomerUser)
        data = {
            'members': [{'id': anonymous.id}],
            'admins': [{'id': anonymous.id}],
            'delete_admins': [{'id': self.tmp_user.id}]
        }
        response = self.client.put(reverse('membersList', kwargs={'room_id': self.chat_room.room_id}),
                                   data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('member', response_json['data']['chat_room_members'])
        self.assertEqual(3, len(response_json['data']['chat_room_members']['member']))
        self.assertIn('admin', response_json['data']['chat_room_members'])
        self.assertEqual(2, len(response_json['data']['chat_room_members']['admin']))
