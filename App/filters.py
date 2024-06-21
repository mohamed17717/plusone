from django_filters import rest_framework as filters

from App import models


class PostFilter(filters.FilterSet):
    tag = filters.CharFilter('tags__slug', lookup_expr='iexact')
    category = filters.CharFilter('categories__slug', lookup_expr='iexact')

    class Meta:
        model = models.Post
        fields = ['tags', 'categories']
