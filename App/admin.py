from django.contrib import admin

from App import models


admin.site.register(models.Post)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Comment)
admin.site.register(models.Vote)
