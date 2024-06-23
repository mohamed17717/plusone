from django.test import TestCase

from App import models
from ._obj_factory import ObjFactory


factory = ObjFactory()


class PostTestCase(TestCase):
    model = models.Post

    def setUp(self):
        self.user1 = factory.get_user('user1')
        self.user2 = factory.get_user('user2')

        self.u1_post = factory.get_post(self.user1, 'title', 'content')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.u1_post.delete()

    def test_computed_fields(self):
        self.assertIsNotNone(self.u1_post.readtime)
        self.assertIsNotNone(self.u1_post.slug)
        self.assertIsNotNone(self.u1_post.search_vector)

    def test_absolute_url(self):
        url = self.u1_post.get_absolute_url()
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_voting(self):
        self.u1_post.upvote(self.user1)
        self.u1_post.upvote(self.user2)

        self.assertEqual(self.u1_post.votes.count(), 2)
        self.assertEqual(self.u1_post.votes_count, 2)

        self.u1_post.downvote(self.user1)
        self.u1_post.downvote(self.user2)

        self.assertEqual(self.u1_post.votes.count(), 2)
        self.assertEqual(self.u1_post.votes_count, -2)


class TagTestCase(TestCase):
    model = models.Tag

    def setUp(self):
        self.tag = factory.get_tag('tag')

    def tearDown(self):
        self.tag.delete()

    def test_computed_fields(self):
        self.assertIsNotNone(self.tag.slug)

    def test_absolute_url(self):
        url = self.tag.get_absolute_url()
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class CategoryTestCase(TestCase):
    model = models.Category

    def setUp(self):
        self.category = factory.get_category('category')

    def tearDown(self):
        self.category.delete()

    def test_computed_fields(self):
        self.assertIsNotNone(self.category.slug)

    def test_absolute_url(self):
        url = self.category.get_absolute_url()
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
