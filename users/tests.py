from unittest.mock import patch

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
    'password': 'n00b',
    'is_verified_mobile': False,
    'is_verified_email': False,

}


def _create_user():
    user = get_user_model().objects.create(**USER_VALID_DATA)
    user.set_password(USER_VALID_DATA['password'])
    user.save()
    return user


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


class TestRegisterUser(TestCase):
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
        self.assertEqual('error', response_json['status'])
        self.assertIn('first_name', response_json['data'])
        self.assertIn('last_name', response_json['data'])
        self.assertIn('password', response_json['data'])

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
        self.assertEqual('error', response_json['status'])
        self.assertIn('mobile_email_field_errors', response_json['data'])

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
        self.assertEqual('error', response_json['status'])
        self.assertIn('message', response_json)
        self.assertIn('mobile', response_json['data'])
        self.assertIn('email', response_json['data'])

    def test_registered_successfully(self):
        with patch('users.utils.generate_email_token') as mock_create_token, \
                patch('users.views.verify_custom_token') as mock_verify_token:
            mock_create_token.return_value = 'MOCK_TOKEN'
            response = self.client.post(
                reverse('user_register'), data=USER_VALID_DATA, format='json')
            # print(f"generate_email_token called: {mock_create_token.called}")

            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response_json['status'], 'ok')
            self.assertEqual(response_json['data']['user']['email'], USER_VALID_DATA['email'])
            self.assertEqual(response_json['data']['user']['mobile'], USER_VALID_DATA['mobile'])
            self.assertEqual(response_json['data']['user']['first_name'], USER_VALID_DATA['first_name'])
            self.assertEqual(response_json['data']['user']['last_name'], USER_VALID_DATA['last_name'])
            self.assertIn('access_token', response_json['data'])
            self.assertIn('Bearer ', response_json['data']['access_token'])

            created_user = get_user_model().objects.filter(
                email=USER_VALID_DATA['email'],
                mobile=USER_VALID_DATA['mobile'],
                first_name=USER_VALID_DATA['first_name'],
                last_name=USER_VALID_DATA['last_name'],
                is_active=False,
            ).first()
            self.assertIsNotNone(created_user)
            mock_verify_token.return_value = (False, {'payload': {"issued_for": 'Verify/Email',
                                                                  "user_id": created_user.id,
                                                                  "email": USER_VALID_DATA['email']}})

            response = self.client.get(
                reverse('user_verify_email', kwargs={'token': 'MOCK_TOKEN'}))
            mock_verify_token.assert_called_once_with('MOCK_TOKEN')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response_json['status'], 'ok')


class TestLoginUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_url_exists(self):
        response = self.client.post(
            reverse('user_login'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_empty_data(self):
        invalid_user_data = {
        }
        response = self.client.post(
            reverse('user_login'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('Invalid input.', response_json['message'])
        self.assertIn('email_mobile', response_json['data'])
        self.assertIn('password', response_json['data'])

    def test_rejects_invalid_email(self):
        invalid_user_data = {
            "email_mobile": "8590410@gmail.com",
            "password": "123456"
        }
        response = self.client.post(
            reverse('user_login'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('Email/Mobile or password is incorrect', response_json['message'])
        self.assertIn('login', response_json['code'])

    def test_rejects_invalid_password(self):
        invalid_user_data = {
            "email_mobile": "mldtavakkoli@gmail.com",
            "password": "123456"
        }
        response = self.client.post(
            reverse('user_login'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('Email/Mobile or password is incorrect', response_json['message'])
        self.assertIn('login', response_json['code'])

    def test_successfully_login(self):
        valid_user_data = {
            "email_mobile": self.user.email,
            "password": USER_VALID_DATA['password']
        }
        response = self.client.post(
            reverse('user_login'), data=valid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('access_token', response_json['data'])
        self.assertIn('Bearer ', response_json['data']['access_token'])


class TestVerifyMobileUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_rejects_not_authenticated_user(self):
        response = self.client.post(
            reverse('user_verify_mobile'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_invalid_otp(self):
        invalid_user_data = {
            "otp": "00000"
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('user_verify_mobile'), data=invalid_user_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('OTP is not valid', response_json['message'])
        self.assertIn('otp', response_json['code'])

    def test_successful_verify_mobile(self):
        # check this workflow in Resend verify mobile
        pass


class TestResendVerifyMobileUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_rejects_not_authenticated_user(self):
        response = self.client.post(
            reverse('user_resend_verify_mobile'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_resend_otp_verify(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('user_resend_verify_mobile'), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response_json)
        self.assertEqual('ok', response_json['status'])

    def test_resend_and_verify_mobile(self):
        MOCK_OTP = "12345"
        with patch('users.utils.create_mobile_otp') as create_mobile_otp:
            create_mobile_otp.return_value = MOCK_OTP
            self.client.force_authenticate(self.user)
            response = self.client.get(
                reverse('user_resend_verify_mobile'), data={}, format='json')
            valid_user_data = {
                "otp": MOCK_OTP
            }
            response = self.client.post(
                reverse('user_verify_mobile'), data=valid_user_data, format='json')
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('status', response_json)
            self.assertEqual('ok', response_json['status'])


class TestResendVerifyEmailUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_rejects_not_authenticated_user(self):
        response = self.client.post(
            reverse('user_resend_verify_email'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_resend_email_verify(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('user_resend_verify_email'), data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response_json)
        self.assertEqual('ok', response_json['status'])

    def test_resend_and_verify_email(self):
        with patch('users.utils.generate_email_token') as mock_create_token, \
                patch('users.views.verify_custom_token') as mock_verify_token:
            mock_create_token.return_value = 'MOCK_TOKEN'
            mock_verify_token.return_value = (False, {'payload': {"issued_for": 'Verify/Email',
                                                                  "user_id": self.user.id,
                                                                  "email": self.user.email}})
            self.client.force_authenticate(self.user)
            response = self.client.get(
                reverse('user_resend_verify_email'), data={}, format='json')

            response = self.client.get(
                reverse('user_verify_email', kwargs={'token': 'MOCK_TOKEN'}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogoutUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_rejects_not_authenticated_user(self):
        response = self.client.post(
            reverse('user_logout'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_logout(self):
        self.client.login(username=self.user.email, password=USER_VALID_DATA['password'])
        self.client.get(
            reverse('user_logout'), data={}, format='json')
        response = self.client.get(
            reverse('user_logout'), data={}, format='json')
        self.assertTrue(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSendOtpLoginUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_exist_send_otp_login(self):
        response = self.client.post(
            reverse('user_send_otp_login'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_invalid_data_otp_login(self):
        invalid_data = {
            'mobile': "09358590410"
        }
        response = self.client.post(
            reverse('user_send_otp_login'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('error', response_json['status'])

    def test_successful_send_otp_login(self):
        valid_data = {
            'mobile': USER_VALID_DATA['mobile']
        }
        response = self.client.post(
            reverse('user_send_otp_login'), data=valid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response_json)
        self.assertEqual('ok', response_json['status'])


class TestVerifyOtpLoginUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_exist_api(self):
        response = self.client.post(
            reverse('user_verify_otp_login'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_empty_data(self):
        invalid_data = {
        }
        response = self.client.post(
            reverse('user_verify_otp_login'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('Invalid input.', response_json['message'])
        self.assertIn('otp', response_json['data'])
        self.assertIn('mobile', response_json['data'])

    def test_rejects_invalid_otp(self):
        MOCK_OTP = "12345"
        invalid_data = {
            'mobile': USER_VALID_DATA['mobile'],
            'otp': "00000"
        }
        with patch('users.utils.create_mobile_otp') as create_mobile_otp:
            create_mobile_otp.return_value = MOCK_OTP
            self.client.post(reverse('user_send_otp_login'), data={'mobile': USER_VALID_DATA['mobile']}, format='json')
            response = self.client.post(reverse('user_verify_otp_login'), data=invalid_data, format='json')
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response_json['status'])
            self.assertIn('OTP is not valid', response_json['message'])
            self.assertIn('otp', response_json['code'])

    def test_successful_login_with_otp(self):
        MOCK_OTP = "12345"
        valid_data = {
            'mobile': USER_VALID_DATA['mobile'],
            'otp': MOCK_OTP
        }
        with patch('users.utils.create_mobile_otp') as create_mobile_otp:
            create_mobile_otp.return_value = MOCK_OTP
            self.client.post(reverse('user_send_otp_login'), data={'mobile': USER_VALID_DATA['mobile']}, format='json')
            response = self.client.post(reverse('user_verify_otp_login'), data=valid_data, format='json')
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('ok', response_json['status'])
            self.assertIn('access_token', response_json['data'])
            self.assertIn('Bearer ', response_json['data']['access_token'])


class TestSendForgetPasswordUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_exist_api(self):
        response = self.client.post(
            reverse('send_forget_password'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_empty_data(self):
        invalid_data = {}
        response = self.client.post(
            reverse('send_forget_password'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('Invalid input.', response_json['message'])
        self.assertIn('email_mobile', response_json['data'])

    def test_rejects_invalid_user_mobile(self):
        invalid_data = {
            'email_mobile': "09358590410",  # invalid mobile
        }

        response = self.client.post(reverse('send_forget_password'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('User does not exist', response_json['message'])

    def test_rejects_invalid_user_email(self):
        invalid_data = {
            'email_mobile': "8590410@gmail.com",  # invalid Email
        }
        response = self.client.post(reverse('send_forget_password'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('User does not exist', response_json['message'])

    def test_successful_send_otp_mobile(self):
        valid_data = {
            'email_mobile': USER_VALID_DATA['mobile'],  # invalid mobile
        }

        response = self.client.post(reverse('send_forget_password'), data=valid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])
        self.assertEqual('OTP Sent', response_json['message'])

    def test_successful_send_token_email(self):
        valid_data = {
            'email_mobile': USER_VALID_DATA['email'],  # invalid mobile
        }

        response = self.client.post(reverse('send_forget_password'), data=valid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])
        self.assertEqual('Email Sent', response_json['message'])


class TestVerifyOTPForgetPasswordUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_exist_api(self):
        response = self.client.post(
            reverse('verify_otp_forget_password'), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_empty_data(self):
        invalid_data = {}
        response = self.client.post(
            reverse('verify_otp_forget_password'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('Invalid input.', response_json['message'])
        self.assertIn('mobile', response_json['data'])
        self.assertIn('otp', response_json['data'])
        self.assertIn('password', response_json['data'])

    def test_rejects_invalid_user_mobile(self):
        invalid_data = {
            'mobile': "09358590410",  # invalid mobile
            'otp': "123456",  # invalid mobile
            'password': "PASSWORD",  # invalid mobile

        }
        response = self.client.post(reverse('verify_otp_forget_password'), data=invalid_data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertIn('User does not exist', response_json['message'])

    def test_rejects_invalid_otp(self):
        MOCK_OTP = "12345"
        invalid_data = {
            'mobile': USER_VALID_DATA['mobile'],  # invalid mobile
            'otp': "00000",  # invalid mobile
            'password': "PASSWORD",  # invalid mobile

        }
        with patch('users.utils.create_mobile_otp') as create_mobile_otp:
            create_mobile_otp.return_value = MOCK_OTP
            self.client.post(reverse('send_forget_password'), data={'mobile': USER_VALID_DATA['mobile']}, format='json')
            response = self.client.post(reverse('verify_otp_forget_password'), data=invalid_data, format='json')
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response_json['status'])
            self.assertIn('OTP is not valid', response_json['message'])
            self.assertIn('otp', response_json['code'])

    def test_successful_changed_password(self):
        MOCK_OTP = "12345"
        new_password = "PASSWORD"
        valid_data = {
            'mobile': USER_VALID_DATA['mobile'],  # invalid mobile
            'otp': MOCK_OTP,  # invalid mobile
            'password': new_password,  # invalid mobile

        }
        with patch('users.utils.create_mobile_otp') as create_mobile_otp:
            create_mobile_otp.return_value = MOCK_OTP
            self.client.post(reverse('send_forget_password'), data={'mobile': USER_VALID_DATA['mobile']}, format='json')
            response = self.client.post(reverse('verify_otp_forget_password'), data=valid_data, format='json')
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('ok', response_json['status'])
        

            # checks user can log in with new password
            self.client.login(username=self.user.mobile, password=new_password)
            response = self.client.get(
                reverse('user_logout'), data={}, format='json')
            self.assertTrue(response.status_code, status.HTTP_200_OK)


class TestVerifyEmailForgetPasswordUser(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_exist_api(self):
        response = self.client.get(
            reverse('verify_email_forget_password', kwargs={"token": "SOME_TEXT_HERE"}), data={}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_invalid_token(self):
        response = self.client.get(
            reverse('verify_email_forget_password', kwargs={"token": "SOME_TEXT_HERE"}), data={}, format='json')
        response_json = response.json()
        print(response_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_json['status'])
        self.assertEqual('Token expired', response_json['message'])
        self.assertEqual('token_error', response_json['code'])

    def test_verify_email_forget_password(self):
        new_password = "PASSw0rd"
        valid_data = {
            "password": new_password
        }
        with patch('users.utils.generate_email_token') as mock_create_token, \
                patch('users.views.verify_custom_token') as mock_verify_token:
            mock_create_token.return_value = 'MOCK_TOKEN'
            self.client.post(reverse('send_forget_password'), data={'email_mobile': USER_VALID_DATA['email']},
                             format='json')
            mock_verify_token.return_value = (False, {'payload': {"issued_for": 'ForgetPassword/Email',
                                                                  "user_id": self.user.id,
                                                                  "email": self.user.email}})

            response = self.client.post(
                reverse('verify_email_forget_password', kwargs={'token': mock_create_token.return_value}),
                data=valid_data, format='json'
            )
            mock_verify_token.assert_called_once_with('MOCK_TOKEN')
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual('ok', response_json['status'])
            self.assertEqual('Password Changed', response_json['message'])

            self.client.login(username=self.user.email, password=new_password)
            response = self.client.get(
                reverse('user_logout'), data={}, format='json')
            self.assertTrue(response.status_code, status.HTTP_200_OK)
