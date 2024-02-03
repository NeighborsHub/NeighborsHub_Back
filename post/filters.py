import django_filters
from django.db.models import Q
from rest_framework_gis.filters import InBBoxFilter

from .models import Post


class ListPostFilter(django_filters.FilterSet):
    # Define the filter for the OR operation
    hashtag_title = django_filters.CharFilter(method='hashtag_comment_or_post')

    def hashtag_comment_or_post(self, queryset, name, value):
        return (queryset.filter(hashtags__hashtag_title=value) |
                queryset.filter(comment_post__hashtags__hashtag_title=value))

    class Meta:
        model = Post
        fields = ['address_id', 'hashtag_title']
        search_fields = ['title', 'body']
