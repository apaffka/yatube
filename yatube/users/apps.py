from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Class for configuring Users application."""
    name = 'users'
    # By this name we will see app in admin area
    verbose_name = 'Управление пользователями'
