from django.db.models import F

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from App import models, serializers


class PostViewSet(ModelViewSet):
    OWNER_ACTIONS = [
        'create', 'update', 'partial_update', 'destroy',
        'owner_list', 'owner_retrieve'
    ]
    PUBLIC_ACTIONS = ['list', 'retrieve']

    serializer_class = serializers.PostSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_permissions(self):
        permissions = [AllowAny()]
        if self.action in self.OWNER_ACTIONS:
            permissions = [IsAuthenticated()]

        return permissions

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action == 'create':
            serializer_class = serializers.PostSerializer.PostCreate
        elif self.action in ['update', 'partial_update']:
            serializer_class = serializers.PostSerializer.PostUpdate
        elif self.action in ['list', 'owner_list']:
            serializer_class = serializers.PostSerializer.PostList
        elif self.action in ['retrieve', 'owner_retrieve']:
            serializer_class = serializers.PostSerializer.PostRetrieve

        return serializer_class

    def get_queryset(self):
        if self.action in self.OWNER_ACTIONS:
            qs = self.request.user.posts.all()

        else:
            qs = models.Post.objects.filter(draft=False)
            if not self.request.user.is_authenticated:
                qs = qs.filter(private=False)

        if self.action in ['list', 'owner_list']:
            qs = qs.select_related('user', 'user__profile')
        elif self.action in ['retrieve', 'owner_retrieve']:
            qs = (
                qs.select_related('user', 'user__profile')
                  .prefetch_related('tags', 'categories')
            )

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get'], detail=False, url_path='owner/list')
    def owner_list(self, request):
        # NOTE : Needed because drafted posts are not visible from the normal list
        return super().list(request)

    @action(methods=['get'], detail=True, url_path=r'owner/retrieve')
    def owner_retrieve(self, request, slug):
        # NOTE : Needed because drafted posts are not visible from the normal list
        return super().retrieve(request, slug, is_owner=True)

    def retrieve(self, request, is_owner=False, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if is_owner is False:
            # select_for_update to Handle race condition
            request.user.posts.filter(
                pk=response.data['id']).select_for_update().update(views=F('views') + 1)

        return response


class TagList(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()


class CategoryList(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()

