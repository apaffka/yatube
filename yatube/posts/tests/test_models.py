from django.core.cache import cache
from django.test import TestCase
from..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Здесь могли бы быть мы с тобой, но ты спишь, а я пишу код',
        )

    def setUp(self):
        cache.clear()

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        cort = (
            (str(post), post.text[:15]),
            (str(group), group.title)
        )
        for value, expected in cort:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_verbose_name_post_and_group(self):
        """Проверяем, что у моделей корректно работает verbose_name."""
        post = PostModelTest.post
        group = PostModelTest.group
        cort = (
            (post._meta.verbose_name, 'Пост'),
            (post._meta.verbose_name_plural, 'Посты'),
            (group._meta.verbose_name, 'Группа'),
            (group._meta.verbose_name_plural, 'Группы'),
        )
        for value, expected in cort:
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                )

    def test_help_text_post_and_group(self):
        """Проверяем, что у моделей корректно работает help_text."""
        post = PostModelTest.post
        group = PostModelTest.group
        cort = (
            (post._meta.get_field('text').help_text,
             'Введите текст поста'),
            (group._meta.get_field('title').help_text,
             'Группа, к которой будет относиться пост'),
        )
        for value, expected in cort:
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                )
