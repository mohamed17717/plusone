from django.contrib.postgres.search import SearchQuery, SearchVector

from rest_framework.filters import SearchFilter, search_smart_split
from rest_framework.fields import CharField


class FullTextSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        fields = super().get_search_fields(view, request)
        if fields:
            prefixes = ''.join(self.lookup_prefixes.keys())
            fields = [f.strip(prefixes) for f in fields]
        return fields

    def get_raw_search_terms(self, request, search_param):
        # Allow mutiple search query using `,` like you search for 'python django'
        # This will return blogs about 'python' and 'django' but if you write it like
        # 'python, django' this will return all python blogs and all django blogs
        # thanks for `to_raw` function that convert search query to raw query valid for FTS

        value = request.query_params.get(search_param, '')

        field = CharField(trim_whitespace=False, allow_blank=True)
        cleaned_value = field.run_validation(value)
        cleaned_value = cleaned_value.replace(',', '|')
        query = search_smart_split(cleaned_value)

        def to_raw(q):
            def quote(i): return f"'{i.strip()}'"
            def parentheses(i): return f"({i.strip()})"
            def or_join(i): return ' | '.join(i)
            def and_join(i): return ' & '.join(i)
            def is_multiple(i): return ' ' in i
            def multiple_query(i): return parentheses(
                and_join(map(quote, i.split(' '))))

            q = ' '.join(query)
            q = q.split('|')
            q = or_join([
                multiple_query(i) if is_multiple(i) else quote(i) for i in q
            ])
            return q

        if query:
            query = to_raw(query)
            return SearchQuery(query, search_type='raw')

    def _filter_by_exclude(self, request, queryset):
        exclude_terms = self.get_raw_search_terms(
            request, search_param='exclude')
        if exclude_terms:
            queryset = queryset.exclude(search_vector=exclude_terms)
        return queryset

    def _filter_by_include(self, request, queryset):
        search_terms = self.get_raw_search_terms(
            request, search_param='search')
        if search_terms:
            queryset = queryset.filter(search_vector=search_terms)
        return queryset

    def _setup_queryset(self, queryset, search_fields):
        if search_fields and not hasattr(queryset.model, 'search_vector'):
            vector = SearchVector(*search_fields)
            queryset = queryset.annotate(search_vector=vector)

        return queryset

    def filter_queryset(self, request, queryset, view, distinct=True):
        search_fields = self.get_search_fields(view, request)

        queryset = self._setup_queryset(queryset, search_fields)

        queryset = self._filter_by_include(request, queryset)
        queryset = self._filter_by_exclude(request, queryset)

        return queryset.distinct()
