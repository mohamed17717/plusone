from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from Users import models

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions', ]

    class Register(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['username', 'email',
                      'password', 'first_name', 'last_name']

        def create(self, validated_data):
            User = self.Meta.model
            return User.objects.create_user(**validated_data)

    class Update(serializers.ModelSerializer):
        class Meta:
            model = User
            exclude = [
                'username', 'email', 'email_verified',
                'is_staff', 'is_active', 'is_superuser',
            ]

    class Login(serializers.Serializer):
        email = serializers.CharField(required=True)
        password = serializers.CharField(required=True)

        def validate(self, attrs):
            request = self.context.get('request')
            user = authenticate(request, **attrs)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise ValidationError({'error': msg}, code='authorization')

            attrs['user'] = user
            return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    class ProfileUpdate(serializers.ModelSerializer):
        class Meta:
            model = models.Profile
            fields = ['bio', 'picture']

    class ProfileRetrieve(serializers.ModelSerializer):
        user = UserSerializer(read_only=True)

        class Meta:
            model = models.Profile
            fields = '__all__'
