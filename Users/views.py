from django.contrib.auth import login

from rest_framework.permissions import AllowAny
# from rest_framework.viewsets import ...

from knox.views import LoginView as KnoxLoginView

from drf_yasg.utils import swagger_auto_schema

from Users import serializers
from utils.drf.viewsets import RetrieveUpdateViewSet


class LoginAPI(KnoxLoginView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSerializer.Login

    @swagger_auto_schema(request_body=serializers.UserSerializer.Login)
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


class RegisterAPI(KnoxLoginView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = serializers.UserSerializer.Register

    @swagger_auto_schema(request_body=serializers.UserSerializer.Register)
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        login(request, user)
        return super(RegisterAPI, self).post(request, format=None)


class UserProfileAPI(RetrieveUpdateViewSet):
    serializer_class = serializers.ProfileSerializer
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            serializer_class = serializers.ProfileSerializer.ProfileUpdate
        elif self.action == 'retrieve':
            serializer_class = serializers.ProfileSerializer.ProfileRetrieve

        return serializer_class

    def get_object(self):
        return self.request.user.profile

