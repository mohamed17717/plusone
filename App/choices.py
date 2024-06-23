from django.db import models


class VoteType(models.IntegerChoices):
    LIKE = 1
    DISLIKE = -1

# Small comment to test ci/cd
