from django.apps import AppConfig


class PostsConfig(AppConfig):
    """Class for configuring Posts application."""
    name = 'posts'
    # By this name we will see app in admin area
    verbose_name = 'Управление постами пользователей'
