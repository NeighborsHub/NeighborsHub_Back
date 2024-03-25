import time

from django.contrib.gis.geos import Point
from django.template.defaulttags import lorem
from django.test import TestCase
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse

from NeighborsHub.test_function import test_object_attributes_existence
from albums.models import Media
from core.models import Hashtag
from post.models import Post, PostHashtag, Comment, CommentHashtag, LikePost, LikeComment, Category, UserSeenPost
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')

    def test_user_can_see_own_post(self):
        # dummy_user = baker.make(CustomerUser)
        # baker.make(Post, created_by=dummy_user, _quantity=10)
        post = baker.make(Post, created_by=self.user, _quantity=1)
        baker.make(LikePost, post=post[0], created_by=self.user,type='like')
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('user_post_list'), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(1, response_json['data']['posts']['count'])
        self.assertEqual('like', response_json['data']['posts']['results'][0]['user_liked'])


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
        post = baker.make(Post, created_by=self.user, body="#Hello_World")
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
        self.assertEqual(2, PostHashtag.objects.filter(post_id=post.id).count())
        self.assertEqual(3, Hashtag.objects.count())

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
        self.dummy_user = baker.make(CustomerUser)
        post_address = baker.make(Address, location=Point(40.5432, -75.5673), )
        dummy_address = baker.make(Address, location=Point(41.5435, -79.5680), )
        medias = baker.make(Media, 5)
        posts = baker.make(Post, address=post_address, media=medias, _quantity=2, body="#hello_world")
        category = baker.make(Category, title='testing', internal_code='test')
        posts[0].category.add(category)
        posts[1].category.add(category)
        baker.make(Post, address=dummy_address, _quantity=10)
        baker.make(Media, 2)

    def test_api_exists(self):
        response = self.client.get(reverse('post_list'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_paginated_post(self):
        response = self.client.get(reverse('post_list', ), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(12, response_json['data']['posts']['count'])

    def test_user_can_see_neighbors_posts(self):
        params = {'user_latitude': -75.5673, 'user_longitude': 40.5432, 'to_distance': 100}
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(2, response_json['data']['posts']['count'])

    def test_not_exist_null_address(self):
        Address.objects.all().delete()
        response = self.client.get(reverse('post_list'), format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(0, response_json['data']['posts']['count'])

    def test_user_can_filter_by_hashtag(self):
        params = {'hashtag_title': 'hello_world'}
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(2, response_json['data']['posts']['count'])

    def test_successful(self):
        params = {
            'user_latitude': -75.5673, 'user_longitude': 40.5433, 'user_distance': 100,
            'post_latitude': -75.5673, 'post_longitude': 40.5432,
        }
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertIn('count', response_json['data']['posts'])
        self.assertIn('results', response_json['data']['posts'])
        self.assertIn('created_by', response_json['data']['posts']['results'][0])
        self.assertIn('address', response_json['data']['posts']['results'][0])
        self.assertIn('body', response_json['data']['posts']['results'][0])
        self.assertIn('title', response_json['data']['posts']['results'][0])
        self.assertIn('media', response_json['data']['posts']['results'][0])
        self.assertIn('distance', response_json['data']['posts']['results'][0])
        self.assertIn('likes', response_json['data']['posts']['results'][0])
        self.assertIn('category', response_json['data']['posts']['results'][0])
        self.assertIn('user_liked', response_json['data']['posts']['results'][0])
        self.assertEqual(2, response_json['data']['posts']['results'][0]['distance'])
        self.assertEqual(5, len(response_json['data']['posts']['results'][0]['media']))
        self.assertIn('title', response_json['data']['posts']['results'][0]['category'][0])
        self.assertIn('id', response_json['data']['posts']['results'][0]['category'][0])
        self.assertIn('test', response_json['data']['posts']['results'][0]['category'][0]['internal_code'])

    def test_successful_in_bbox(self):
        params = {
            'in_bbox': '40.5432,-75.5673,41.52,-75.55'
        }
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(2, response_json['data']['posts']['count'])

    def test_successful_filter_category(self):
        params = {
            'category': 'test'
        }
        response = self.client.get(reverse('post_list'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(2, response_json['data']['posts']['count'])

    def test_seen_posts_successful(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('post_list'))
        self.assertEqual(UserSeenPost.objects.filter(user=self.user).count(),
                         len(response.json()['data']['posts']['results']))



class TestListCountLocationPost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        address_1 = baker.make(Address, location=Point(40.5432, -75.5673), )
        address_2 = baker.make(Address, location=Point(42.5435, -80.5680), )
        address_3 = baker.make(Address, location=Point(41.5435, -79.5680), )
        baker.make(Post, address=address_1, _quantity=2, body="#hello_world")
        baker.make(Post, address=address_2, _quantity=3)
        baker.make(Post, address=address_3, _quantity=4)

    def test_api_exists(self):
        response = self.client.get(reverse('post_location_count'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_paginated_posts_location(self):
        response = self.client.get(reverse('post_location_count', ), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(3, response_json['data']['posts']['count'])

    def test_location_posts_with_filter_user_location(self):
        data = {'user_longitude': 40.5432, 'user_latitude': -75.5673, 'to_distance': 1000}
        response = self.client.get(reverse('post_location_count', ), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(1, response_json['data']['posts']['count'])

    def test_location_posts_in_bbox(self):
        data = {'in_bbox': '40.5432,-75.5673,41.52,-75.55'}
        response = self.client.get(reverse('post_location_count'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(1, response_json['data']['posts']['count'])


class TsetCommentModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        Comment()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'body', 'updated_at', 'created_at', 'created_by', 'post_id', 'reply_to_id'
        ]
        comment = Comment()
        test_object_attributes_existence(self, comment, attributes)

    def test_comment_create_model(self):
        created_comment = baker.make(Comment)
        test_obj = Comment.objects.filter(id=created_comment.id).first()
        self.assertIsNotNone(test_obj)

    def test_successfully_create_hashtags(self):
        created_comment = baker.make(Comment, body="#Hello, world")
        hashtag = Hashtag.objects.filter(hashtag_title="hello").first()
        hashtag = CommentHashtag.objects.filter(hashtag__hashtag_title="hello", comment_id=created_comment.id).first()
        self.assertIsNotNone(hashtag)


class TestCreateComment(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.post = baker.make(Post)

    def test_api_exists(self):
        response = self.client.post(reverse('create_post_comment',
                                            kwargs={'post_pk': self.post.id}), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_empty_data(self):
        empty_data = {
            'body': None
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('create_post_comment',
                                            kwargs={'post_pk': self.post.id}), data=empty_data, format='json')

        response_json = response.json()
        self.assertEqual('error', response_json['status'])
        self.assertIn('body', response_json['data'])

    def test_successful_create_comment(self):
        data = {
            'body': "This is test for #comment."
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('create_post_comment',
                                            kwargs={'post_pk': self.post.id}), data=data, format='json')

        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(1, Comment.objects.filter(post_id=self.post.id).count())
        self.assertEqual(1, Hashtag.objects.filter(hashtag_title='comment').count())


class TestListComment(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.post = baker.make(Post)
        comment = baker.make(Comment, post=self.post, created_by=self.user)
        reply_comment = baker.make(Comment, post=self.post, reply_to=comment)
        reply_reply = baker.make(Comment, post=self.post, reply_to=reply_comment)

    def test_api_exists(self):
        response = self.client.get(reverse('list_post_comment',
                                           kwargs={'post_pk': self.post.id}), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_list_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('list_post_comment',
                                           kwargs={'post_pk': self.post.id}), data={}, format='json')

        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(1, response_json['data']['comments']['count'])
        self.assertEqual(1, len(response_json['data']['comments']['results'][0]['replies']))
        self.assertEqual(1, len(response_json['data']['comments']['results'][0]['replies'][0]['replies']))
        self.assertTrue(response_json['data']['comments']['results'][0]['is_owner'])
        self.assertFalse(response_json['data']['comments']['results'][0]['replies'][0]['is_owner'])


class TestRetrievePost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.other_user = baker.make(CustomerUser)
        self.post = baker.make(Post, created_by=self.user)

    def test_api_exists(self):
        response = self.client.get(reverse('post_retrieve',
                                           kwargs={'post_pk': self.post.id}), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_list_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('post_retrieve',
                                           kwargs={'post_pk': self.post.id}), data={}, format='json')
        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertTrue(response_json['data']['post']['is_owner'])

    def test_seen_posts_successful(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.get(reverse('post_retrieve', kwargs={'post_pk': self.post.id}))
        response_json = response.json()
        self.assertIn('is_seen', response_json['data']['post'])
        self.assertEqual({}, response_json['data']['post']['is_seen'])

        response = self.client.get(reverse('post_retrieve', kwargs={'post_pk': self.post.id}))
        response_json = response.json()
        self.assertIn('is_seen', response_json['data']['post'])
        self.assertIn('first_seen', response_json['data']['post']['is_seen'])
        self.assertIn('last_seen', response_json['data']['post']['is_seen'])


class TestUpdateRetrieveDeleteComment(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.post = baker.make(Post)
        self.comment = baker.make(Comment, post=self.post, created_by=self.user)

    def test_api_exists(self):
        response = self.client.post(reverse('post_comment_update_delete',
                                            kwargs={
                                                'post_pk': self.post.id, 'comment_pk': self.comment.id
                                            }), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_dummy_user(self):
        dummy_user = baker.make(CustomerUser)
        self.client.force_authenticate(dummy_user)
        response = self.client.get(reverse('post_comment_update_delete',
                                           kwargs={
                                               'post_pk': self.post.id, 'comment_pk': self.comment.id
                                           }), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_update_comment(self):
        data = {
            'body': "This is test for #comment."
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(reverse('post_comment_update_delete',
                                           kwargs={
                                               'post_pk': self.post.id, 'comment_pk': self.comment.id
                                           }), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(1, Comment.objects.filter(post_id=self.post.id, body=data['body']).count())
        self.assertEqual(1, Hashtag.objects.filter(hashtag_title='comment').count())

    def test_successful_retrieve_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('post_comment_update_delete',
                                           kwargs={
                                               'post_pk': self.post.id, 'comment_pk': self.comment.id
                                           }), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(self.comment.body, response_json['data']['comment']['body'])

    def test_successful_delete_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('post_comment_update_delete',
                                              kwargs={
                                                  'post_pk': self.post.id, 'comment_pk': self.comment.id
                                              }), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Comment.objects.filter(id=self.comment.id).first())


class LikePostTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.post = baker.make(Post)

    def test_api_exists(self):
        response = self.client.post(reverse('post_like',
                                            kwargs={'post_pk': self.post.id}), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_likes_successful(self):
        self.client.force_authenticate(self.user)
        data = {'type': 'support'}
        response = self.client.post(reverse('post_like',
                                            kwargs={'post_pk': self.post.id}), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIsNotNone(LikePost.objects.filter(post_id=self.post.id, type='support').first())
        self.assertIsNone(LikePost.objects.filter(post_id=self.post.id, type='like').first())

    def test_user_removes_like_successful(self):
        self.client.force_authenticate(self.user)
        baker.make(LikePost, post_id=self.post.id, created_by=self.user)
        response = self.client.delete(reverse('post_like',
                                              kwargs={'post_pk': self.post.id}), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(LikePost.objects.filter(post_id=self.post.id).first())


class LikeCommentTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.comment = baker.make(Comment)

    def test_api_exists(self):
        response = self.client.post(reverse('comment_like',
                                            kwargs={'comment_pk': self.comment.id}), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_likes_successful(self):
        self.client.force_authenticate(self.user)
        data = {'type': 'support'}
        response = self.client.post(reverse('comment_like',
                                            kwargs={'comment_pk': self.comment.id}), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIsNotNone(LikeComment.objects.filter(comment_id=self.comment.id, type='support').first())

    def test_user_removes_like_successful(self):
        self.client.force_authenticate(self.user)
        baker.make(LikeComment, comment_id=self.comment.id, created_by=self.user)
        response = self.client.delete(reverse('comment_like',
                                              kwargs={'comment_pk': self.comment.id}), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(LikeComment.objects.filter(comment_id=self.comment.id, ).first())


class ListCategory(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        baker.make(Category, _quantity=9)
        self.category = baker.make(Category, title="testing", internal_code='test')

    def test_api_exist(self):
        response = self.client.get(reverse('list_category'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_categories(self):
        response = self.client.get(reverse('list_category'), data={'search': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(1, response_json['data']['categories']['count'])


class ListPublicUserPost(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        post_address = baker.make(Address, location=Point(40.5432, -75.5673), )
        medias = baker.make(Media, 5)
        posts = baker.make(Post, address=post_address, media=medias, _quantity=1,
                           body="#hello_world", created_by=self.user, updated_by=self.user)

        category = baker.make(Category, title='testing', internal_code='test')
        posts[0].category.add(category)
        baker.make(Post, _quantity=10, body="#bye_world", )

    def test_user_can_paginated_post(self):
        response = self.client.get(reverse('public_user_post_list', kwargs={'user_pk': self.user.id}),
                                   data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(1, response_json['data']['posts']['count'])


class TsetUserSeenPostModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        UserSeenPost()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'user_id', 'post_id', 'first_seen', 'last_seen',
        ]
        obj = UserSeenPost()
        test_object_attributes_existence(self, obj, attributes)

    def test_create_obj(self):
        created = baker.make(UserSeenPost)
        test_obj = UserSeenPost.objects.filter(id=created.id).first()
        self.assertIsNotNone(test_obj)
