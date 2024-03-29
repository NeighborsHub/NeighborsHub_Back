from django.urls import path

from core.views import ListCountryView, ListStateView, ListCityView, ListHashtagsView, CreateFeedbackView

urlpatterns = [
    path('base/countries', ListCountryView.as_view(), name='core_list_country'),
    path('base/states', ListStateView.as_view(), name='core_list_state'),
    path('base/cities', ListCityView.as_view(), name='core_list_city'),
    path('base/hashtags', ListHashtagsView.as_view(), name='core_list_hashtags'),
    path('base/feedback', CreateFeedbackView.as_view(), name='core_create_feedback'),
]
