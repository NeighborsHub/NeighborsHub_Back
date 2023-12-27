from django.template.defaulttags import lorem
from django.test import TestCase
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse

from NeighborsHub.test_function import test_object_attributes_existence
from core.models import Hashtag
from post.models import Post
from users.models import Address
from users.tests import _create_user
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


class TsetPostModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        Post()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'state', 'updated_at', 'created_at', 'created_by', 'title', 'body'
        ]
        post = Post()
        test_object_attributes_existence(self, post, attributes)

    def test_user_model(self):
        created_post = baker.make(Post)
        test_obj = Post.objects.filter(id=created_post.id).first()
        self.assertIsNotNone(test_obj)

    def test_successfully_create_hashtags(self):
        created_post = baker.make(Post, body="#Hello, world")
        test_obj = Post.objects.filter(id=created_post.id).first()
        hashtag = Hashtag.objects.filter(hashtag_title="hello").first()
        self.assertIsNotNone(hashtag)


class TestCreatePost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.address = baker.make(Address, user=self.user)

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.post(reverse('user_post_create'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_empty_data(self):
        empty_data = {
            'title': None,
            'body': None,
            'address_id': None,
            'media': []
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('user_post_create'), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid input.')
        self.assertIn('title', response_json['data'])
        self.assertIn('body', response_json['data'])
        self.assertIn('address_id', response_json['data'])

    def test_successful_create_post(self):
        media_file1 = SimpleUploadedFile("media.jpg", b"file_content....", content_type="image/jpeg")

        valid_data = {
            'title': 'Lorem Ipsum',
            'body': '#Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut '
                    '#labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco '
                    ' laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit '
                    ' in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat '
                    ' cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'address_id': self.address.id,
            'medias': [media_file1],
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('user_post_create'), valid_data, format='multipart')
        response_json = response.json()
        print(response_json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('ok', response_json['status'])
        self.assertIn(valid_data['title'], response_json['data'])
        self.assertIn(valid_data['body'], response_json['data'])
