import datetime

import django_filters
from django.db.models import Q
from rest_framework_gis.filters import InBBoxFilter
from django.utils import timezone

from .models import Post


class ListPostFilter(django_filters.FilterSet):
    # Define the filter for the OR operation
    category = django_filters.CharFilter(field_name='category__internal_code')
    hashtag_title = django_filters.CharFilter(method='hashtag_comment_or_post')
    from_days = django_filters.NumberFilter(method='from_days_method')
    is_seen = django_filters.BooleanFilter()

    def hashtag_comment_or_post(self, queryset, name, value):
        return (queryset.filter(hashtags__hashtag_title=value) |
                queryset.filter(comment_post__hashtags__hashtag_title=value))

    def from_days_method(self, queryset, name, value):
        try:
            value = int(value)
            time_before = timezone.now() - datetime.timedelta(days=value)
            return queryset.filter(created_at__lte=time_before)
        except ValueError:
            return queryset

    class Meta:
        model = Post
        fields = ['address_id', 'hashtag_title', 'from_days', 'category', 'is_seen']
        search_fields = ['title', 'body']
