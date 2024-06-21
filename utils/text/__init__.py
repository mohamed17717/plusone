import uuid

from django.utils.text import slugify


def unique_slugify(model, text, lookup_name='slug'):
    slug = slugify(text)
    suffix = str(uuid.uuid4()).split('-')[0]
    unique_slug = f'{slug}-{suffix}'

    lookup = {lookup_name: unique_slug}
    while model.objects.filter(**lookup).exists():
        suffix = uuid.uuid4().hex.split('-')[-1]
        unique_slug = f'{slug}-{suffix}'
        lookup = {lookup_name: unique_slug}

    return unique_slug
