from django.db import models
# from django.contrib.auth import get_user_model
from users.models import User
from .fields import HexColorField
from django.core.validators import MinValueValidator


class Ingredients(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=100,
                            verbose_name='Название',
                            blank=False)
    units = models.CharField(max_length=25,
                             verbose_name='Единицы измерения',
                             blank=False)

    class Meta:
        constraints = models.UniqueConstraint(
            fields=['name', 'units'],
            name='unique_ingredients',
        ),
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name='Название',
                            blank=False)
    color = HexColorField(unique=True,
                          verbose_name='HEX-код цвета',
                          blank=False)
    slug = models.SlugField(unique=True,
                            blank=False,
                            verbose_name='Слаг/Slug')

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=False,
                               verbose_name='Автор',
                               related_name='recipes')
    name = models.CharField(max_length=200,
                            blank=False,
                            verbose_name='Название')
    image = models.ImageField(verbose_name='Фото блюда',
                              upload_to='recipes/')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredients,
                                         verbose_name='Ингредиенты')
    tag = models.ManyToManyField(Tags,
                                 verbose_name='Теги',
                                 related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Время приготовление должно быть больше нуля!'
        ),),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('pub_date',)


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='recipe_favorite')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='user_favorite')

    class Meta:
        constraints = models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorite_recipe',
        ),
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-id',)

    def __str__(self) -> str:
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='shopping_user')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепты',
                               related_name='shopping_recipe')

    class Meta:
        constraints = models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_list',
        ),
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        return f'{self.recipe} в списке покупок у пользователя {self.user}.'


class IngredientsInRecipe(models.Model):
    """Модель ингредиентов в рецептах."""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='iir',
                               verbose_name='рецепт'
                               )
    ingredient = models.ForeignKey(Ingredients,
                                   on_delete=models.CASCADE,
                                   related_name='iir',
                                   verbose_name='ингредиент')
    amount = models.DecimalField(max_digits=6,
                                 decimal_places=2,
                                 verbose_name='Количество',
                                 blank=False,
                                 validators=(MinValueValidator(
                                     1,
                                     message='Введите число большее нуля!'
                                 ),))

    class Meta:
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'ingredient',),
            name='recipe_ingredients_exists'
        )),
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} – {self.amount}'
