from django.db.models.signals import post_save
from django.dispatch import receiver

from Users import models


@receiver(post_save, sender=models.User)
def on_create_user_create_profile(sender, instance, created, **kwargs):
    if not created:
        return

    models.Profile.objects.create(user=instance)
