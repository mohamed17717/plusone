from django.db import models


class VoteType(models.IntegerChoices):
    LIKE = 1
    DISLIKE = -1
