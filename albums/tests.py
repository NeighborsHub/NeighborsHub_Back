from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.reverse import reverse
from model_bakery import baker
from rest_framework import status

from NeighborsHub.test_function import test_object_attributes_existence
from albums.models import Media, UserAvatar
from users.tests import _create_user
from rest_framework.test import APIClient


class TestMediaModel(TestCase):
    def test_model_exist(self):
        Media()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'file', 'updated_at', 'created_at', 'created_by', 'updated_by'
        ]
        media = Media()
        test_object_attributes_existence(self, media, attributes)

    def test_media_model(self):
        created_media = baker.make(Media)
        test_obj = Media.objects.filter(id=created_media.id).first()
        self.assertIsNotNone(test_obj)


class TestMyListMedias(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.medias = baker.make(Media, created_by=self.user, _quantity=12)
        baker.make('post.Post', media=self.medias)

    def test_exist_api(self):
        response = self.client.get(reverse('media_mylist'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('media_mylist'))
        response_json = response.json()
        print(response_json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('medias', response_json['data'])
        self.assertIn('count', response_json['data']['medias'])
        self.assertIn('next', response_json['data']['medias'])
        self.assertIn('previous', response_json['data']['medias'])
        self.assertIn('results', response_json['data']['medias'])
        self.assertIn('id', response_json['data']['medias']['results'][0])
        self.assertIn('file', response_json['data']['medias']['results'][0])
        self.assertIn('created_at', response_json['data']['medias']['results'][0])
        self.assertIn('post', response_json['data']['medias']['results'][0])
        self.assertIn('id', response_json['data']['medias']['results'][0]['post'])
        self.assertIn('title', response_json['data']['medias']['results'][0]['post'])
        self.assertIn('body', response_json['data']['medias']['results'][0]['post'])


class TestUserListMedias(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.medias = baker.make(Media, created_by=self.user, _quantity=12)
        baker.make('post.Post', media=self.medias)

    def test_exist_api(self):
        response = self.client.get(reverse('media_user_list', kwargs={'user_pk': self.user.id}))
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful(self):
        response = self.client.get(reverse('media_user_list', kwargs={'user_pk': self.user.id}))
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('medias', response_json['data'])
        self.assertIn('count', response_json['data']['medias'])
        self.assertIn('next', response_json['data']['medias'])
        self.assertIn('previous', response_json['data']['medias'])
        self.assertIn('results', response_json['data']['medias'])
        self.assertIn('id', response_json['data']['medias']['results'][0])
        self.assertIn('file', response_json['data']['medias']['results'][0])
        self.assertIn('created_at', response_json['data']['medias']['results'][0])
        self.assertIn('post', response_json['data']['medias']['results'][0])
        self.assertIn('id', response_json['data']['medias']['results'][0]['post'])
        self.assertIn('title', response_json['data']['medias']['results'][0]['post'])
        self.assertIn('body', response_json['data']['medias']['results'][0]['post'])
        self.assertIn('first_name', response_json['data']['medias']['results'][0]['created_by'])
        self.assertIn('last_name', response_json['data']['medias']['results'][0]['created_by'])
        self.assertIn('email', response_json['data']['medias']['results'][0]['created_by'])
        self.assertIn('mobile', response_json['data']['medias']['results'][0]['created_by'])


class TestMyListAvatar(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.medias = baker.make(UserAvatar, created_by=self.user, user=self.user, _quantity=12)

    def test_exist_api(self):
        response = self.client.get(reverse('avatar_mylist'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_list_avatar(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('avatar_mylist'))
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])

    # def test_successful_creat_avatar(self):
    #     media_file1 = SimpleUploadedFile("avatar.jpg", b"1", content_type="image/jpeg")
    #     input_data = {'avatar': media_file1}
    #     self.client.force_authenticate(self.user)
    #     response = self.client.post(reverse('avatar_mylist'), data=input_data, format='multipart')
    #     response_json = response.json()
    #     print(response_json)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual('ok', response_json['status'])
