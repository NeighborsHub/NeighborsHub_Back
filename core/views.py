import datetime

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter

from NeighborsHub.custom_view_mixin import ExpressiveListModelMixin
from core.models import Country, State, City, Hashtag
from core.serializers import CountrySerializer, StateSerializer, CitySerializer, HashtagSerializer


class ListCountryView(ExpressiveListModelMixin, generics.ListAPIView):
    plural_name = "countries"
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = None


class ListStateView(ExpressiveListModelMixin, generics.ListAPIView):
    plural_name = "states"
    queryset = State.objects.all()
    serializer_class = StateSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['country_id']
    search_fields = ['name']


class ListCityView(ExpressiveListModelMixin, generics.ListAPIView):
    plural_name = "cities"
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['state_id', 'state__country_id']
    search_fields = ['name']


class ListHashtagsView(ExpressiveListModelMixin, generics.ListAPIView):
    plural_name = "hashtags"
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
