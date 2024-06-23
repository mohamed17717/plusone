from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from knox.models import AuthToken

from App import models
from ._obj_factory import ObjFactory


factory = ObjFactory()


def knox_authorize(user, test_case):
    token = AuthToken.objects.create(user)[1]
    test_case.client.credentials(HTTP_AUTHORIZATION='Token ' + token)


class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = factory.get_user('test_user1')
        self.user2 = factory.get_user('test_user2')

        self.category = factory.get_category('test_category')
        self.tag = factory.get_tag('test_tag')

        knox_authorize(self.user1, self)

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_create(self):
        data = {
            'title': 'test_title',
            'content': 'test_content',
            'categories': [self.category.id],
            'tags': [self.tag.id]
        }

        endpoint = reverse('app:post-list')
        response = self.client.post(endpoint, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = models.Post.objects.get(pk=response.data['id'])
        self.assertEqual(post.user, self.user1)
        self.assertEqual(post.title, 'test_title')
        self.assertEqual(post.content, 'test_content')
        self.assertEqual(post.categories.first(), self.category)
        self.assertEqual(post.tags.first(), self.tag)

    def test_update(self):
        data = {
            'title': 'updated_test_title',
            'content': 'updated_test_content',
            'categories': [self.category.id],
            'tags': [self.tag.id]
        }

        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.patch(endpoint, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post = models.Post.objects.get(pk=post.id)
        self.assertEqual(post.user, self.user1)
        self.assertEqual(post.title, 'updated_test_title')
        self.assertEqual(post.content, 'updated_test_content')
        self.assertEqual(post.categories.first(), self.category)
        self.assertEqual(post.tags.first(), self.tag)

    def test_delete(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.delete(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_retrieve(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_private_post(self):
        post = factory.get_post(self.user2, 'test_title',
                                'test_content', private=True)
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_draft_post(self):
        post = factory.get_post(self.user2, 'test_title',
                                'test_content', draft=True)
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list(self):
        endpoint = reverse('app:post-list')
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_list_by_category(self):
        endpoint = reverse('app:post-list')
        response = self.client.get(
            f'{endpoint}?category={self.category.slug}', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.category.posts.count())

    def test_filter_list_by_tag(self):
        endpoint = reverse('app:post-list')
        response = self.client.get(
            f'{endpoint}?tag={self.tag.slug}', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.tag.posts.count())

    def test_search_list(self):
        factory.get_post(self.user1, 'test_title', 'mhmd is good')
        endpoint = reverse('app:post-list') + '?search=mhmd'
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_delete_not_owned_post(self):
        post = factory.get_post(self.user2, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.delete(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_not_owned_post(self):
        data = {
            'title': 'updated_test_title',
            'content': 'updated_test_content',
            'categories': [self.category.id],
            'tags': [self.tag.id]
        }

        post = factory.get_post(self.user2, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.patch(endpoint, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_retrieve(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-owner-retrieve',
                           kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_owner_retrieve(self):
        post = factory.get_post(self.user2, 'test_title', 'test_content')
        endpoint = reverse('app:post-owner-retrieve',
                           kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upvote(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-upvote', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.client.get(endpoint, format='json')
        self.client.get(endpoint, format='json')
        self.client.get(endpoint, format='json')
        self.client.get(endpoint, format='json')

        self.assertEqual(post.votes_count, 1)

    def test_downvote(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-downvote', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.client.get(endpoint, format='json')
        self.client.get(endpoint, format='json')
        self.client.get(endpoint, format='json')
        self.client.get(endpoint, format='json')

        self.assertEqual(post.votes_count, -1)

    def test_comment(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:post-comment', kwargs={'slug': post.slug})
        response = self.client.post(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_on_closed_comment_post(self):
        post = factory.get_post(self.user1, 'test_title',
                                'test_content', open_comments=False)
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:post-comment', kwargs={'slug': post.slug})
        response = self.client.post(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_list(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        for i in range(5):
            factory.get_comment(self.user1, post, 'test_comment')

        endpoint = reverse('app:post-comment-list', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)


class PostAnonymousAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = factory.get_user('test_user1')

        self.category = factory.get_category('test_category')
        self.tag = factory.get_tag('test_tag')

    def tearDown(self):
        self.user1.delete()

    def test_create(self):
        data = {
            'title': 'test_title',
            'content': 'test_content',
            'categories': [self.category.id],
            'tags': [self.tag.id]
        }

        endpoint = reverse('app:post-list')
        response = self.client.post(endpoint, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update(self):
        data = {
            'title': 'updated_test_title',
            'content': 'updated_test_content',
            'categories': [self.category.id],
            'tags': [self.tag.id]
        }

        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.patch(endpoint, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.delete(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_private_post(self):
        post = factory.get_post(self.user1, 'test_title',
                                'test_content', private=True)
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_draft_post(self):
        post = factory.get_post(self.user1, 'test_title',
                                'test_content', draft=True)
        endpoint = reverse('app:post-detail', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list(self):
        endpoint = reverse('app:post-list')
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_list_by_category(self):
        endpoint = reverse('app:post-list')
        response = self.client.get(
            f'{endpoint}?category={self.category.slug}', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.category.posts.count())

    def test_filter_list_by_tag(self):
        endpoint = reverse('app:post-list')
        response = self.client.get(
            f'{endpoint}?tag={self.tag.slug}', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.tag.posts.count())

    def test_search_list(self):
        factory.get_post(self.user1, 'test_title', 'mhmd is good')
        endpoint = reverse('app:post-list') + '?search=mhmd'
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_owner_retrieve(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-owner-retrieve',
                           kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upvote(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-upvote', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_downvote(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        endpoint = reverse('app:post-downvote', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:post-comment', kwargs={'slug': post.slug})
        response = self.client.post(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_list(self):
        post = factory.get_post(self.user1, 'test_title', 'test_content')
        for i in range(5):
            factory.get_comment(self.user1, post, 'test_comment')

        endpoint = reverse('app:post-comment-list', kwargs={'slug': post.slug})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)


class TagAPITestCase(APITestCase):
    def test_list(self):
        n = 8
        for i in range(n):
            factory.get_tag('test_tag' + str(i))

        endpoint = reverse('app:tag-list')
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], n)


class CategoryAPITestCase(APITestCase):
    def test_list(self):
        n = 8
        for i in range(n):
            factory.get_category('test_category' + str(i))

        endpoint = reverse('app:category-list')
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], n)


class CommentAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = factory.get_user('test_user1')
        self.user2 = factory.get_user('test_user2')

        self.post = factory.get_post(self.user1, 'test_title', 'test_content')
        self.comment = factory.get_comment(
            self.user1, self.post, 'test_comment')

        knox_authorize(self.user1, self)

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_update(self):
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:comment-detail',
                           kwargs={'pk': self.comment.pk})
        response = self.client.patch(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'This is amazing post')

    def test_delete(self):
        endpoint = reverse('app:comment-detail',
                           kwargs={'pk': self.comment.pk})
        response = self.client.delete(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_not_owned_comment(self):
        comment = factory.get_comment(self.user2, self.post, 'test_comment')
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:comment-detail',
                           kwargs={'pk': comment.pk})
        response = self.client.patch(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_not_owned_comment(self):
        comment = factory.get_comment(self.user2, self.post, 'test_comment')
        endpoint = reverse('app:comment-detail',
                           kwargs={'pk': comment.pk})
        response = self.client.delete(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reply(self):
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:comment-reply',
                           kwargs={'pk': self.comment.pk})
        response = self.client.post(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_replies_list(self):
        for i in range(5):
            factory.get_reply(self.user1, self.comment, 'test_comment')

        endpoint = reverse('app:comment-replies-list',
                           kwargs={'pk': self.comment.pk})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)


class CommentAnonymousAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = factory.get_user('test_user1')
        self.user2 = factory.get_user('test_user2')

        self.post = factory.get_post(self.user1, 'test_title', 'test_content')
        self.comment = factory.get_comment(
            self.user1, self.post, 'test_comment')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_update(self):
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:comment-detail',
                           kwargs={'pk': self.comment.pk})
        response = self.client.patch(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, 401)

    def test_delete(self):
        endpoint = reverse('app:comment-detail',
                           kwargs={'pk': self.comment.pk})
        response = self.client.delete(endpoint, format='json')

        self.assertEqual(response.status_code, 401)

    def test_reply(self):
        comment_data = {
            'content': 'This is amazing post'
        }
        endpoint = reverse('app:comment-reply',
                           kwargs={'pk': self.comment.pk})
        response = self.client.post(endpoint, comment_data, format='json')

        self.assertEqual(response.status_code, 401)

    def test_replies_list(self):
        for i in range(5):
            factory.get_reply(self.user1, self.comment, 'test_comment')

        endpoint = reverse('app:comment-replies-list',
                           kwargs={'pk': self.comment.pk})
        response = self.client.get(endpoint, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
