from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    def __str__(self):
        return self.title
    title = models.CharField(
        'group title',
        max_length=200,
        help_text='Группа, к которой будет относиться пост')
    slug = models.SlugField('group link name', unique=True, max_length=50)
    description = models.TextField('group description', max_length=200)

    class Meta:
        ordering = ['title']
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    def __str__(self):
        # post text output
        return self.text[:15]

    text = models.TextField('post data', help_text='Введите текст поста')
    pub_date = models.DateTimeField('publish date', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    text = models.TextField(
        'comment text',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        'creation date',
        auto_now_add=True,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )