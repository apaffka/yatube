# Generated by Django 2.2.16 on 2022-03-12 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Фолловер', 'verbose_name_plural': 'Фолловеры'},
        ),
    ]
