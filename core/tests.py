from django.test import TestCase
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from NeighborsHub.test_function import test_object_attributes_existence
from core.models import Country, State, City, Hashtag, Feedback
from post.models import Post


class TestCountryModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        Country()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = ['name', 'code', 'name_code', 'population', 'capital', 'location', 'phone_code', 'emoji']
        country = Country()
        test_object_attributes_existence(self, country, attributes)

    def test_address_model_create_successful(self):
        created_country = baker.make(Country)
        test_obj = Country.objects.filter(id=created_country.id).first()
        self.assertIsNotNone(test_obj)


class TestStateModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        State()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = ['name', 'name_code', 'abbreviation', 'capital', 'location', 'country_id']
        state = State()
        test_object_attributes_existence(self, state, attributes)

    def test_address_model_create_successful(self):
        created_state = baker.make(State)
        test_obj = State.objects.filter(id=created_state.id).first()
        self.assertIsNotNone(test_obj)


class TestCityModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        City()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = ['name', 'name_code', 'population', 'location', 'state_id']
        city = City()
        test_object_attributes_existence(self, city, attributes)

    def test_address_model_create_successful(self):
        created_city = baker.make(City)
        test_obj = State.objects.filter(id=created_city.id).first()
        self.assertIsNotNone(test_obj)


class TestListCountry(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        baker.make(Country, _quantity=5)

    def test_exist_api(self):
        response = self.client.get(reverse('core_list_country'), format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful(self):
        response = self.client.get(reverse('core_list_country'), format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])


class TestListState(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        country = baker.make(Country)
        baker.make(State, _quantity=5)
        self.state = baker.make(State, country=country)

    def test_exist_api(self):
        response = self.client.get(reverse('core_list_state'), format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful(self):
        response = self.client.get(reverse('core_list_state'), format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])

    def test_successful_filter(self):
        response = self.client.get(reverse('core_list_state'), {'country_id': self.state.country_id}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])


class TestListCity(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        country = baker.make(Country)
        baker.make(City, _quantity=5)
        self.state = baker.make(State, country=country)
        self.city = baker.make(City, state=self.state)

    def test_exist_api(self):
        response = self.client.get(reverse('core_list_city'), format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful(self):
        response = self.client.get(reverse('core_list_city'), format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])

    def test_successful_filter(self):
        response = self.client.get(reverse('core_list_city'),
                                   {'state_id': self.state.id, 'state__country_id': self.state.country_id
                                    },
                                   format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])


class TestListHashtags(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        baker.make(Hashtag, hashtag_title='hello')
        baker.make(Post, _quantity=10, body='#hello')

    def test_exist_api(self):
        response = self.client.get(reverse('core_list_hashtags'), format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful(self):
        params = {
            "search": "hell"
        }
        response = self.client.get(reverse('core_list_hashtags'), data=params, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ok', response_json['status'])
        self.assertEqual(1, len(response_json['data']['hashtags']['results']))
        self.assertEqual('hello', response_json['data']['hashtags']['results'][0]['hashtag_title'])
        self.assertEqual(10, response_json['data']['hashtags']['results'][0]['count'])


class TestFeedbackModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        Feedback()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = ['name', 'email', 'message', 'created_at', 'updated_at', 'state_id']
        obj = Feedback()
        test_object_attributes_existence(self, obj, attributes)

    def test_address_model_create_successful(self):
        created_obj = baker.make(Feedback)
        test_obj = Feedback.objects.filter(id=created_obj.id).first()
        self.assertIsNotNone(test_obj)


class TestCreateFeedback(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_exist_api(self):
        response = self.client.post(reverse('core_create_feedback'), format='json')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_empty_data(self):
        data = {}
        response = self.client.post(reverse('core_create_feedback'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('error', response_json['status'])
        self.assertIn('message', response_json['data'])
        self.assertIn('name', response_json['data'])
        self.assertIn('email', response_json['data'])

    def test_successful(self):
        data = {
            "name": "Milad",
            "email": "8590410@gmail.com",
            "message": "Lorem ipsum dolor sit amet, consectetur"
        }
        response = self.client.post(reverse('core_create_feedback'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('message', response_json['data']['feedback'])
        self.assertIn('name', response_json['data']['feedback'])
        self.assertIn('email', response_json['data']['feedback'])