from django.urls import path

from knox import views as knox_views

from Users import views


app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path('login/', views.LoginAPI.as_view(), name='knox_login'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),

    path('profile/', views.UserProfileAPI.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='profile'),
]
