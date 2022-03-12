from django.test import Client, TestCase
from ..models import Post, Follow, User
from django.urls import reverse
from django.core.cache import cache


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logined_user1 = User.objects.create_user(username='Oleg')
        cls.logined_user2 = User.objects.create_user(username='Misha')

        cls.post = Post.objects.create(
            author=cls.logined_user1,
            text='Проверим подписки',
        )

    def setUp(self):
        cache.clear()
        self.post_author_user = Client()
        self.site_auth_user = Client()
        self.post_author_user.force_login(self.logined_user1)
        self.site_auth_user.force_login(self.logined_user2)

    def test_post_in_follow_list_for_follower(self):
        """Проверяем, что пост в ленте подписок у фоловера."""
        self.follow = Follow.objects.create(
            user=self.logined_user2, author=self.post.author
        )
        response = self.site_auth_user.get(reverse('posts:follow_index'))
        expect = Follow.objects.filter(user=self.logined_user1)
        self.assertTrue(response.context['post_list'], expect)

    def test_post_in_follow_list_for_follower(self):
        """Проверяем, что поста нет в подписках, если не фоловер."""
        response = self.site_auth_user.get(reverse('posts:follow_index'))
        expect = Follow.objects.filter(user=self.logined_user1)
        obj = response.context['page_obj'].object_list
        self.assertFalse(obj, expect)

    def test_auth_user_can_follow(self):
        """Проверяем, что авторизованный пользователь может подписаться."""
        follow_count = Follow.objects.count()
        self.follow = Follow.objects.create(
            user=self.logined_user2, author=self.post.author
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
