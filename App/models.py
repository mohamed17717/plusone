import readtime
import humanize
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

from App import choices
from utils.text import unique_slugify


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
            self.slug = unique_slugify(Post, self.title)
            self.readtime = self.get_readtime()

        return super().save(*args, **kwargs)

    def get_readtime(self):
        estimation = readtime.of_markdown(self.content)
        delta = timedelta(seconds=estimation.seconds)

        return humanize.naturaldelta(delta)

    def get_absolute_url(self):
        return resolve_url('app:post-detail', self.slug)


class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(blank=True, null=True, unique=True, db_index=True)
    posts_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            self.slug = unique_slugify(Category, self.name)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return resolve_url('app:post-list') + f'?category={self.slug}'


class Tag(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(blank=True, null=True, unique=True, db_index=True)
    posts_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            self.slug = unique_slugify(Tag, self.name)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return resolve_url('app:post-list') + f'?tag={self.slug}'


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
