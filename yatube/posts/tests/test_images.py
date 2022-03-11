import shutil
import tempfile

from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.file1 = SimpleUploadedFile(
            name='ara.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестируем группу',
            slug='any_slug',
            description='Тут мы всё опишем',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='NoNameUser'),
            text='Я памятник, пока что просто камень',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.posts_count = Post.objects.count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.post_author = Client()
        self.post_author.force_login(self.post.author)

    def test_image_go_to_post_with_content(self):
        """Проверка, что изображение идёт в контексте на нужные страницы."""
        data_form = {
            'text': 'Тестовый заголовок',
            'group': self.group.id,
            'image': self.uploaded,
        }
        reversed_pages = (
            reverse('posts:main_view'),
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}
                    ),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ),
        )
        for reverse_name in reversed_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.post(
                    reverse_name,
                    data=data_form,
                    follow=True,
                )
                if 'page_obj' in response.context:
                    obj = response.context['page_obj'][0]
                    self.assertEqual(obj.image, self.post.image)
                    self.assertTrue(
                        Post.objects.filter(
                            image=f'posts/{self.uploaded.name}'
                        ).exists()
                    )
                else:
                    obj = response.context['post']
                    self.assertEqual(obj.image, self.post.image)
                    self.assertTrue(
                        Post.objects.filter(
                            image=f'posts/{self.uploaded.name}'
                        ).exists()
                    )

    def test_post_form_image_create_position_in_database(self):
        data_dict = {
            'text': 'И снова тесты',
            'group': self.group.id,
            'image': self.file1,
        }
        response = self.post_author.post(
            reverse('posts:post_create'),
            data=data_dict,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.post.author})
                             )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
