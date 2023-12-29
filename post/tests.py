from django.contrib.gis.geos import Point
from django.template.defaulttags import lorem
from django.test import TestCase
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse

from NeighborsHub.test_function import test_object_attributes_existence
from albums.models import Media
from core.models import Hashtag
from post.models import Post
from users.models import Address, CustomerUser
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
        media_file2 = SimpleUploadedFile("media.jpg", b"file_content....", content_type="image/jpeg")

        valid_data = {
            'title': 'Lorem Ipsum',
            'body': '#Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut '
                    '#labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',
            'address_id': self.address.id,
            'medias': [media_file1, media_file2],
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('user_post_create'), valid_data, format='multipart')
        response_json = response.json()
        print(response_json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('post', response_json['data'])
        self.assertIn('address', response_json['data']['post'])
        self.assertIn('title', response_json['data']['post'])
        self.assertIn('body', response_json['data']['post'])
        self.assertIn('created_at', response_json['data']['post'])
        self.assertIn('media', response_json['data']['post'])

        self.assertEqual(len(valid_data['medias']), Media.objects.all().count())
        self.assertEqual(2, Hashtag.objects.all().count())
        self.assertEqual(1, Post.objects.all().count())


class TestMyListPost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.address = baker.make(Address, user=self.user)

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('user_post_list'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_api(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('user_post_list'), data={}, format='json')
        response_json = response.json()
        print(response_json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')

    def test_user_can_see_own_post(self):
        dummy_user = baker.make(CustomerUser)
        baker.make(Post, created_by=dummy_user, _quantity=10)
        baker.make(Post, created_by=self.user, _quantity=1)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('user_post_list'), data={}, format='json')
        response_json = response.json()
        print(response_json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(1, response_json['data']['posts']['count'])


class TestUpdateDeleteRetrievePost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.address = baker.make(Address, user=self.user)
        baker.make(Post)

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('user_post_update_retrieve_delete', kwargs={'pk': 1}), data={},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_owner_object(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('user_post_update_retrieve_delete', kwargs={'pk': 1}), data={},
                                   format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json['status'], 'error')

    def test_retrieve_post_for_user(self):
        post = baker.make(Post, created_by=self.user)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('user_post_update_retrieve_delete', kwargs={'pk': post.id}),
                                   data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')

    def test_update_post(self):
        post = baker.make(Post, created_by=self.user)
        media_file1 = SimpleUploadedFile("media.jpg", b"file_content....", content_type="image/jpeg")
        media_file2 = SimpleUploadedFile("media.jpg", b"file_content....", content_type="image/jpeg")
        valid_data = {
            'title': 'Lorem Ipsum',
            'body': '#Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut '
                    '#labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco ',
            'address_id': self.address.id,
            'medias': [media_file1, media_file2],
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(reverse('user_post_update_retrieve_delete', kwargs={'pk': post.id}),
                                   data=valid_data, format='multipart')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(valid_data['title'], response_json['data']['post']['title'])
        self.assertEqual(len(valid_data['medias']), len(response_json['data']['post']['media']))
        self.assertEqual(2, Hashtag.objects.count())

    def test_delete_post(self):
        post = baker.make(Post, created_by=self.user)
        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('user_post_update_retrieve_delete', kwargs={'pk': post.id}),
                                      data={}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Post.objects.filter(id=post.id).first())


class TestListPost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        post_address = baker.make(Address, location=Point(-75.5673, 40.5432), )
        dummy_address = baker.make(Address, location=Point(-79.5680, 41.5435), )
        baker.make(Post, address=post_address, _quantity=2, body="#hello_world")
        baker.make(Post, address=dummy_address, _quantity=10)

    def test_api_exists(self):
        response = self.client.get(reverse('post_list'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_paginated_post(self):
        response = self.client.get(reverse('post_list', ), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(10, response_json['data']['posts']['count'])

    def test_user_can_see_neighbors_posts(self):
        params = {'longitude': -75.5673, 'latitude': 40.5432, 'distance': 100}
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(2, response_json['data']['posts']['count'])

    def test_user_can_filter_by_hashtag(self):
        params = {'hashtags__hashtag_title': 'hello_world'}
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(2, response_json['data']['posts']['count'])
