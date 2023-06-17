# Generated by Django 3.2.19 on 2023-06-17 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0004_auto_20230617_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='tags',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Слаг/Slug'),
        ),
    ]
