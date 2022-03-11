from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        """Smoke test для главной страницы."""
        self.guest_client = Client()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='NoNameUser'),
            text='Здесь могли бы быть мы с тобой, но ты спишь, а я пишу код',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_correct_template_for_urls(self):
        """URLs используют правильный шаблон."""
        urls_and_templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html'
        }
        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

    def test_correct_template_for_edit(self):
        """Проверяем, что posts/<int:post_id>/edit/ использует шаблон
        posts/create_post.html.
        """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertEqual(response.status_code, 200)

    def test_correct_template_for_create(self):
        """Проверяем, что posts/create/ использует шаблон
        posts/create_post.html.
        """
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertEqual(response.status_code, 200)

    def test_if_page_not_exist_404(self):
        """Проверка вывода 404, если неправильный адрес"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
