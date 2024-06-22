from django.contrib import admin

from App import models


class CustomModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [
            field.name for field in model._meta.fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)


admin.site.register(models.Post, CustomModelAdmin)
admin.site.register(models.Category, CustomModelAdmin)
admin.site.register(models.Tag, CustomModelAdmin)
admin.site.register(models.Comment, CustomModelAdmin)
admin.site.register(models.Vote, CustomModelAdmin)
