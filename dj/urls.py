from django.contrib import admin
from django.urls import path, include
from django.conf import settings



urlpatterns = [
    path('user/', include('Users.urls', namespace='users')),
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]
