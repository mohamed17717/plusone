from django.db.models import F

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable
from rest_framework import status

from App import models, serializers

from utils.drf.viewsets import RetrieveUpdateDeleteViewSet


class PostViewSet(ModelViewSet):
    OWNER_ACTIONS = [
        'create', 'update', 'partial_update', 'destroy',
        'owner_list', 'owner_retrieve'
    ]
    AUTHORIZED_ACTIONS = ['upvote', 'downvote']
    PUBLIC_ACTIONS = ['list', 'retrieve']

    serializer_class = serializers.PostSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_permissions(self):
        permissions = [AllowAny()]
        if self.action in self.OWNER_ACTIONS + self.AUTHORIZED_ACTIONS:
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
            qs = qs.select_related(
                'user', 'user__profile').prefetch_related('votes')
        elif self.action in ['retrieve', 'owner_retrieve']:
            qs = (
                qs.select_related('user', 'user__profile')
                  .prefetch_related('tags', 'categories', 'votes')
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

    @action(methods=['get'], detail=True, url_path=r'upvote')
    def upvote(self, request, slug):
        post = self.get_object()
        models.Vote.objects.update_or_create(
            user=request.user, post=post, defaults={'type': models.Vote.VoteType.LIKE})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True, url_path=r'downvote')
    def downvote(self, request, slug):
        post = self.get_object()
        models.Vote.objects.update_or_create(
            user=request.user, post=post, defaults={'type': models.Vote.VoteType.DISLIKE})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path=r'comment')
    def comment(self, request, slug):
        post = self.get_object()

        serializer = serializers.CommentSerializer.CommentCreate(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, post=post)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True, url_path=r'comment/list')
    def comment_list(self, request, slug):
        post = self.get_object()

        qs = post.comments.all().filter(comment__isnull=True).select_related(
            'user', 'user__profile')
        serializer = serializers.CommentSerializer.CommentList
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, is_owner=False, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if is_owner is False:
            # select_for_update to Handle race condition
            request.user.posts.filter(
                pk=response.data['id']).select_for_update().update(views=F('views') + 1)

        return response


class TagListAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()


class CategoryListAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()


class CommentViewSet(RetrieveUpdateDeleteViewSet):
    OWNER_ACTIONS = [
        'retrieve', 'update', 'partial_update', 'destroy',
    ]
    PUBLIC_ACTIONS = ['replies_list', 'reply']

    serializer_class = serializers.CommentSerializer

    def get_permissions(self):
        permissions = [AllowAny()]
        if self.action in self.OWNER_ACTIONS:
            permissions = [IsAuthenticated()]

        return permissions

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action in self.OWNER_ACTIONS:
            serializer_class = serializers.CommentSerializer.CommentUpdate
        elif self.action == 'replies_list':
            serializer_class = serializers.CommentSerializer.CommentList

        return serializer_class

    def get_queryset(self):
        if self.action in self.OWNER_ACTIONS:
            qs = self.request.user.comments.all()

        elif self.action in self.PUBLIC_ACTIONS:
            qs = models.Comment.objects.all()
        else:
            raise NotAcceptable('Comment not support this action')
        return qs

    @action(methods=['get'], detail=True, url_path=r'replies/list')
    def replies_list(self, request, *args, **kwargs):
        queryset = self.get_object().replies.all().select_related(
            'user', 'user__profile')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path=r'reply')
    def reply(self, request, pk):
        comment = self.get_object()

        serializer = serializers.CommentSerializer.CommentCreate(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, post=comment.post, comment=comment)

        return Response(status=status.HTTP_204_NO_CONTENT)
