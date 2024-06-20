from django.contrib.auth import login

from rest_framework.permissions import AllowAny

from knox.views import LoginView as KnoxLoginView

from Users import serializers


class LoginAPI(KnoxLoginView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSerializer.Login

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

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        login(request, user)
        return super(RegisterAPI, self).post(request, format=None)


# RUViewSet
# from common.utils.drf.viewsets import RUViewSet
# class UserProfileAPI(APIView):
#     def get_serializer_class(self):
#         serializer_class = serializers.UserSerializer

#         if self.action == 'update':
#             serializer_class = serializers.UserSerializer.Update
#         elif self.action == 'retrieve':
#             pass

#         return serializer_class

#     def get_object(self):
#         return self.request.user
