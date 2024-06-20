from django.contrib import admin

# Register your models here.
from Users import models

admin.site.register(models.User)
admin.site.register(models.Profile)
