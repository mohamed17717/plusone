from rest_framework import serializers

from App import models


class CategorySerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = models.Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = models.Tag
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        exclude = ['search_vector']

    class PostCreate(serializers.ModelSerializer):
        url = serializers.ReadOnlyField(source='get_absolute_url')

        class Meta:
            model = models.Post
            exclude = ['readtime', 'slug', 'views', 'search_vector']
            extra_kwargs = {'user': {'read_only': True}}

    class PostUpdate(serializers.ModelSerializer):
        class Meta:
            model = models.Post
            exclude = [
                'user', 'readtime', 'slug', 'views', 'search_vector'
            ]

    class PostList(serializers.ModelSerializer):
        author = serializers.SerializerMethodField()
        url = serializers.ReadOnlyField(source='get_absolute_url')
        votes = serializers.ReadOnlyField(source='votes_count')

        def get_author(self, obj):
            from Users.serializers import ProfileSerializer
            serializer_class = ProfileSerializer.ProfileRetrieve
            return serializer_class(obj.user.profile).data

        class Meta:
            model = models.Post
            exclude = ['content', 'search_vector']

    class PostRetrieve(PostList):
        tags = TagSerializer(many=True, read_only=True)
        categories = CategorySerializer(many=True, read_only=True)

        class Meta:
            model = models.Post
            exclude = ['search_vector']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'

    class CommentCreate(serializers.ModelSerializer):
        class Meta:
            model = models.Comment
            fields = '__all__'
            extra_kwargs = {
                'user': {'read_only': True},
                'post': {'read_only': True},
                'comment': {'read_only': True},
            }

    class CommentUpdate(serializers.ModelSerializer):
        class Meta:
            model = models.Comment
            fields = ['content']

    class CommentList(serializers.ModelSerializer):
        author = serializers.SerializerMethodField()

        def get_author(self, obj):
            from Users.serializers import ProfileSerializer
            serializer_class = ProfileSerializer.ProfileRetrieve
            return serializer_class(obj.user.profile).data

        class Meta:
            model = models.Comment
            fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vote
        fields = '__all__'
