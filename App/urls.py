from django.urls import path, include

from rest_framework.routers import DefaultRouter

from App import views


app_name = 'app'

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')


urlpatterns = [
    path('tags/', views.TagListAPI.as_view()),
    path('categories/', views.CategoryListAPI.as_view()),
    # path('comment/<int:pk>/', views.CommentOwnerAPI.as_view()),

    path('', include(router.urls)),
]
