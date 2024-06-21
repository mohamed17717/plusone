import uuid
import readtime
import humanize
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.shortcuts import resolve_url

from App import choices


User = get_user_model()


class Post(models.Model):
    # Relations
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')

    # Content
    title = models.CharField(max_length=128)
    content = models.TextField()
    image = models.ImageField(upload_to='posts', blank=True, null=True)

    # Content Describe
    readtime = models.CharField(max_length=128, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True, db_index=True)

    # statistics
    views = models.IntegerField(default=0)

    # flags
    draft = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    open_comments = models.BooleanField(default=True)

    # SEO fields
    description = models.CharField(max_length=255, blank=True, null=True)

    categories = models.ManyToManyField(
        'Category', related_name='posts', blank=True)
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            self.slug = self.get_unique_slug()
            self.readtime = self.get_readtime()

        return super().save(*args, **kwargs)

    def get_unique_slug(self):
        slug = slugify(self.title)
        suffix = str(uuid.uuid4()).split('-')[0]
        unique_slug = f'{slug}-{suffix}'

        while Post.objects.filter(slug=unique_slug).exists():
            suffix = uuid.uuid4().hex.split('-')[-1]
            unique_slug = f'{slug}-{suffix}'

        return unique_slug

    def get_readtime(self):
        estimation = readtime.of_markdown(self.content)
        delta = timedelta(seconds=estimation.seconds)

        return humanize.naturaldelta(delta)

    def get_absolute_url(self):
        return resolve_url('app:post-detail', self.slug)


class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(blank=True, null=True)
    posts_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(blank=True, null=True)
    posts_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')

    comment = models.ForeignKey(
        'Comment', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_updated(self):
        return self.created_at != self.updated_at


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    type = models.SmallIntegerField(choices=choices.VoteType.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'post']]
