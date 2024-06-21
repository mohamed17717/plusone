from django.urls import path, include

from rest_framework.routers import DefaultRouter

from App import views


app_name = 'app'

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')


urlpatterns = [
    path('tags/', views.TagList.as_view()),
    path('categories/', views.CategoryList.as_view()),
    path('', include(router.urls)),
]
