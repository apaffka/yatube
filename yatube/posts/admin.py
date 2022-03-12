from django.contrib import admin
# import Post and Group models from models
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    """Configures the display of Post model data in admin area."""
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Configures the display of Group model data in admin area."""
    list_display = ('pk',
                    'title',
                    'slug')


class CommentAdmin(admin.ModelAdmin):
    """Configures the display of Comment model data in admin area."""
    list_display = ('pk',
                    'text',
                    'created',
                    'post',
                    'author')


class FollowAdmin(admin.ModelAdmin):
    """Configures the display of Follow model data in admin area."""
    list_display = ('pk',
                    'user',
                    'author')


# Registering models Post and Group in admin area
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
