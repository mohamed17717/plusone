from rest_framework import serializers

from App import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'

    class PostCreate(serializers.ModelSerializer):
        url = serializers.ReadOnlyField(source='get_absolute_url')

        class Meta:
            model = models.Post
            exclude = [
                'readtime', 'slug', 'views',
            ]
            extra_kwargs = {
                'user': {'read_only': True},
            }

    class PostUpdate(serializers.ModelSerializer):
        class Meta:
            model = models.Post
            exclude = [
                'user', 'readtime', 'slug', 'views',
            ]

    class PostList(serializers.ModelSerializer):
        author = serializers.SerializerMethodField()
        url = serializers.ReadOnlyField(source='get_absolute_url')

        def get_author(self, obj):
            from Users.serializers import ProfileSerializer
            serializer_class = ProfileSerializer.ProfileRetrieve
            return serializer_class(obj.user.profile).data

        class Meta:
            model = models.Post
            exclude = ['content']

    class PostRetrieve(serializers.ModelSerializer):
        author = serializers.SerializerMethodField()
        tags = TagSerializer(many=True, read_only=True)
        categories = CategorySerializer(many=True, read_only=True)

        def get_author(self, obj):
            from Users.serializers import ProfileSerializer
            serializer_class = ProfileSerializer.ProfileRetrieve
            return serializer_class(obj.user.profile).data

        class Meta:
            model = models.Post
            fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vote
        fields = '__all__'
