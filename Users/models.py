from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from Users.tasks import send_email


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    email_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def send_email(self, subject, message, confirmed_only=False):
        if confirmed_only and self.email_verified is False:
            raise ValidationError('Email is not verified.')

        send_email.delay(subject, message, [self.email])


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField(max_length=255, blank=True, null=True)
    picture = models.ImageField(
        upload_to='profile_pictures', null=True, blank=True)

    def __str__(self):
        return self.user.email
