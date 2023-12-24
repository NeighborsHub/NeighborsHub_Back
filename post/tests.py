from django.test import TestCase
from model_bakery import baker

from NeighborsHub.test_function import test_object_attributes_existence
from core.models import Hashtag
from post.models import Post


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
