from django.test import Client, TestCase
from ..models import Post, Group, User
from ..views import POSTS_PER_PAGE
from django.urls import reverse
from django.core.cache import cache


PAGES_FOR_TEST = POSTS_PER_PAGE + 5


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='MyHeart')
        cls.author = User.objects.get(username='MyHeart')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group = Group.objects.get(slug='test-slug')
        for i in range(PAGES_FOR_TEST):
            Post.objects.create(
                author=cls.author,
                text=f'Коси и забивай {i}',
                group=cls.group,
            )
        cls.template_pages = (
            reverse('posts:main_view'),
            reverse('posts:group_list',
                    kwargs={'slug': cls.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': cls.author}),
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверка 1 стр паджинатора для index, group_list и profile."""
        for page_name in self.template_pages:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверка 2 стр паджинатора для index, group_list и profile."""
        for page_name in self.template_pages:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    (PAGES_FOR_TEST - POSTS_PER_PAGE)
                )
