from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель пользователя для данного проекта."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = {
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    }
    role = models.CharField(choices=ROLES,
                            max_length=10,
                            verbose_name='Роль пользователя',
                            default=USER)
    email = models.EmailField(unique=True,
                              max_length=254,
                              verbose_name='Адрес email',
                              blank=False)
    username = models.CharField(unique=True,
                                max_length=150,
                                verbose_name='Логин',
                                blank=False)
    password = models.CharField(max_length=150,
                                blank=False,
                                verbose_name='Пароль')
    first_name = models.CharField(max_length=150,
                                  blank=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150,
                                 blank=False,
                                 verbose_name='Фамилия')

    @property
    def is_moderator(self):
        return self.is_staff or self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    def __str__(self):
        return self.username


class Subscribtion(models.Model):
    """Модель подписки на автора."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='following')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_sub',
        ),

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
