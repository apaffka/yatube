from django.test import Client, TestCase
from ..models import Post, Group, User, Comment
from django.urls import reverse
from django import forms
from django.core.cache import cache


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='Kesha')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='NoNameUser'),
            text='Здесь могли бы быть мы с тобой',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.post_author_user = Client()
        self.authenticated_user = Client()
        self.post_author_user.force_login(self.post.author)
        self.authenticated_user.force_login(self.auth_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:main_view'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Проверяем, что в шаблоны index, group_list и profile
        приходит нужный контент.
        """
        template_pages = (
            reverse('posts:main_view'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.post.author}),
        )
        for page_name in template_pages:
            with self.subTest(page_name=page_name):
                response = self.post_author_user.get(page_name)
                first_object = response.context['page_obj'][0]
                task_text_0 = first_object.text
                task_author_0 = first_object.author
                task_group_0 = first_object.group
                self.assertEqual(task_text_0, self.post.text)
                self.assertEqual(task_author_0, self.post.author)
                self.assertEqual(task_group_0, self.post.group)

    def test_create_post_form_show_correct_context(self):
        """"Проверяем, что шаблон create_post получает верный контекст."""
        template_pages = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        )
        for page in template_pages:
            with self.subTest(page=page):
                response = self.post_author_user.get(page)
                form_data = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for item, expected in form_data.items():
                    with self.subTest(item=item):
                        form_field = response.context.get(
                            'form').fields.get(item)
                        self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Проверяем, что шаблон post_detail получает верный контекст."""
        response = self.post_author_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        field = response.context['post']
        expected = self.post
        self.assertEqual(field, expected)

    def test_post_is_in_correct_group(self):
        """Проверяем, что пост попал в правильную группу."""
        response = self.post_author_user.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
        )
        field = response.context['page_obj']
        expected = self.post
        self.assertIn(expected, field)

    def test_post_can_comment_only_authorized_user(self):
        """Проверяем, что посты могут комментировать только
        авторизованные пользователи.
        """
        comment_count = Comment.objects.count()
        test_data = {
            'text': 'Словами не передать какой комментарий'
        }
        response = self.authenticated_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=test_data,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_guest_can_not_comment(self):
        """Проверяем, что гость не комментирует."""
        comment_count = Comment.objects.count()
        test_data = {
            'text': 'А я не авторизован и хочу комментировать'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=test_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/')
        self.assertEqual(Comment.objects.count(), comment_count)
