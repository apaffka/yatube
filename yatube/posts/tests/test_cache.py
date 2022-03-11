from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Post, Group, Comment

User = get_user_model()


class PostsCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа тестовых групп',
            slug='test-slug-slug',
            description='Давайте опишем'
        )
        cls.post1 = Post.objects.create(
            author=User.objects.create_user(username='Masha'),
            text='Новый тест',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_cache(self):
        """Проверяем, что посты на главной странице кешируютсяю."""
        response0 = self.guest_client.get(reverse('posts:main_view')).content
        self.post1.delete()
        response1 = self.guest_client.get(reverse('posts:main_view')).content
        self.assertEqual(response0, response1)
        cache.clear()
        response2 = self.guest_client.get(reverse('posts:main_view')).content
        self.assertNotEqual(response1, response2)
