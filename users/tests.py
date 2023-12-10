from django.contrib.auth import get_user_model
from django.test import TestCase
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse

from NeighborsHub.test_function import test_object_attributes_existence
from users.models import CustomerUser
from rest_framework.test import APIClient

USER_VALID_DATA = {
    'mobile': '09373875028',
    'email': 'mldtavakkoli@gmail.com',
    'first_name': 'Milad',
    'last_name': 'Tavakoli',
    'password': 'NeighborsHub',
    'birth_date': '25-02-1994'

}


class TestUserModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        CustomerUser()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'email', 'username', 'mobile', 'first_name', 'last_name', 'birth_date', 'is_active', 'state',
            'updated_at', 'created_at'
        ]
        user = CustomerUser()
        test_object_attributes_existence(self, user, attributes)

    def test_user_model_knows_the_consumer_profile_type(self):
        created_user = baker.make(get_user_model())
        test_obj = CustomerUser.objects.filter(id=created_user.id).first()
        self.assertIsNotNone(test_obj)


class RegisterUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_url_exists(self):
        response = self.client.post(
            reverse('user_register'), data=USER_VALID_DATA, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_empty_data(self):
        invalid_user_data = {
        }
        response = self.client.post(
            reverse('user_register'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response_json)
        self.assertIn('last_name', response_json)
        self.assertIn('password', response_json)

    def test_rejects_empty_email_and_mobile(self):
        invalid_user_data = {
            'first_name': 'Milad',
            'last_name': 'Tavakoli',
            'password': 'noob'
        }
        response = self.client.post(
            reverse('user_register'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mobile_email_field_errors', response_json)

    def test_rejects_invalid_mobile_email(self):
        invalid_user_data = {
            'first_name': 'Milad',
            'last_name': 'Tavakoli',
            'password': 'noob',
            'email': '8590410',
            'mobile': 'o9373875'
        }
        response = self.client.post(
            reverse('user_register'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mobile', response_json)
        self.assertIn('email', response_json)

    def test_registered_successfully(self):
        response = self.client.post(
            reverse('user_register'), data=USER_VALID_DATA, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['data']['user']['email'], USER_VALID_DATA['email'])
        self.assertEqual(response_json['data']['user']['mobile'], USER_VALID_DATA['mobile'])
        self.assertEqual(response_json['data']['user']['first_name'], USER_VALID_DATA['first_name'])
        self.assertEqual(response_json['data']['user']['last_name'], USER_VALID_DATA['last_name'])

        created_user = get_user_model().objects.filter(
            email=USER_VALID_DATA['email'],
            mobile=USER_VALID_DATA['mobile'],
            first_name=USER_VALID_DATA['first_name'],
            last_name=USER_VALID_DATA['last_name'],
            is_active=False,
        ).first()

        self.assertIsNotNone(created_user)
