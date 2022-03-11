from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='Vasya')

        cls.group = Group.objects.create(
            title='Группа для тестов',
            slug='slug_test',
            description='Описание группы',
        )

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='Misha'),
            text='Здесь могли бы быть мы с тобой',
            group=cls.group,
            )

        cls.post_count = Post.objects.count()

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.post_author = Client()
        self.post_author.force_login(self.post.author)
        self.any_authorized_user = Client()
        self.any_authorized_user.force_login(self.auth_user)

    def test_post_was_created(self):
        """Проверка того, что пост был создан и попал в нужную группу.
        Проверка редиректа.
        """
        form_data = {
            'text': 'Пишу текст в свой новый пост',
            'group': self.group.id,
        }
        response = self.post_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.post.author})
                             )
        expected = Post.objects.all().last()
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        self.assertEqual(expected.group.slug, self.post.group.slug)

    def test_valid_edit_form_changed_post(self):
        """Проверяем, что при редактировании поста проиcходит его изменение."""
        new_data_form = {
            'text': 'Меняю текст своего поста',
            'group': self.group.id,
        }
        response = self.post_author.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=new_data_form,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id})
                             )
        expected = Post.objects.all().last()
        self.assertEqual(Post.objects.count(), self.post_count)
        self.assertEqual(expected.text, new_data_form['text'])

    def test_create_post_by_anonymous(self):
        """Проверяем, что при создании поста анонимным пользователем
        не изменяется кол-во постов в БД.
        """
        new_data_form = {
            'text': 'Я аноним и хочу создать пост',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=new_data_form,
            follow=True,
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), self.post_count)

    def test_edit_post_by_anonymous(self):
        """Проверяем, что при редактировании поста анонимным пользователем
        не изменяются значения полей поста.
        """
        new_data_form = {
            'text': 'Я аноним и хочу редактировать пост',
            'group': 'any_group',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ),
            data=new_data_form,
            follow=True,
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        expected = Post.objects.all().last()
        self.assertEqual(expected.text, self.post.text)
        self.assertEqual(expected.group.slug, self.post.group.slug)

    def test_edit_post_by_authorized_but_not_author(self):
        """Проверяем, что при редактировании поста не автором
        пост не изменяет значение полей.
        """
        new_data_form = {
            'text': 'Я Вася и я хочу редактировать пост',
            'group': 'any_group',
        }
        response = self.any_authorized_user.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=new_data_form,
            follow=True,
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')
        expected = Post.objects.all().last()
        self.assertEqual(expected.text, self.post.text)
        self.assertEqual(expected.group.slug, self.post.group.slug)
