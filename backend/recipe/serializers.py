from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import (Ingredients,
                     Tags,
                     IngredientsInRecipe,
                     Recipe,
                     FavoriteRecipe,
                     ShoppingList,
                     TagsRecipe)
from drf_base64.fields import Base64ImageField
from users.models import User


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для авторов."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class IngredientsSerializer(serializers.ModelSerializer):
    """"Сериализатор для модели ингредиентов."""

    class Meta:
        model = Ingredients
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        model = Tags
        fields = '__all__'


class ShowIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    # amount = serializers.ReadOnlyField(source='ingredient.amount')

    class Meta:
        model = IngredientsInRecipe
        fields = '__all__'


class IngredientRecipeSaveSerializer(serializers.Serializer):
    """Сериализатор для сохранения ингредиентов в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tags.objects.all()
    )
    author = AuthorSerializer(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    ingredients = IngredientRecipeSaveSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author', 'ingredients',)

    def to_representation(self, value):
        data = RecipeSerializer(value, context={'request': self.context.get(
            'request')}).data
        return data

    def create(self, validated_data):
        tags_list = validated_data.pop('tags')
        ingredient_list = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        existing_ingredients = {}

        for item in ingredient_list:
            ingredient = get_object_or_404(Ingredients, id=item.get('id'))
            amount = item['amount']

            if ingredient.id in existing_ingredients:
                amount_ex = existing_ingredients[ingredient.id]
                IngredientsInRecipe.objects.filter(
                    ingredient=ingredient,
                    recipe=recipe,
                    amount=amount_ex
                ).delete()

                IngredientsInRecipe.objects.create(
                    ingredient=ingredient,
                    recipe=recipe,
                    amount=amount + amount_ex
                )
                existing_ingredients[ingredient.id] = amount
            else:

                IngredientsInRecipe.objects.create(
                    ingredient=ingredient,
                    recipe=recipe,
                    amount=amount
                )
            existing_ingredients[ingredient.id] = amount

        for item in tags_list:
            TagsRecipe.objects.create(
                tag=item,
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')

        tags_list = validated_data.pop('tags')
        instance.tags.set(tags_list)
        existing_ingredients = {}
        ingredient_list = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for item in ingredient_list:
            ingredient = get_object_or_404(Ingredients, id=item.get('id'))
            amount = item['amount']

            if ingredient.id in existing_ingredients:
                amount_ex = existing_ingredients[ingredient.id]

                instance.ingredients.remove(ingredient)

                instance.ingredients.add(
                    ingredient,
                    through_defaults={'amount': (amount_ex + amount)}
                )

                existing_ingredients[ingredient.id] = amount + amount_ex
            else:
                instance.ingredients.add(
                    ingredient,
                    through_defaults={'amount': amount}
                )
                existing_ingredients[ingredient.id] = amount

        instance.save()
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    def __init__(self, *args, **kwargs):
        super(RecipeSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        self.fields['author'].context['request'] = request

    tags = TagsSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = ShowIngredientsInRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and bool(obj.lover.filter(user=user))

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and bool(obj.buyer.filter(user=user))


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранного."""

    id = serializers.CharField(
        read_only=True, source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True, source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True, source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True, source='recipe.name',
    )

    class Meta:
        model = FavoriteRecipe
        fields = ['id',
                  'cooking_time',
                  'name',
                  'image']

    def validate(self, data):
        recipe = data['recipe']
        user = data['user']
        if user == recipe.author:
            raise serializers.ValidationError('Вы автор рецепта!')
        if (FavoriteRecipe.objects.filter(recipe=recipe, user=user).exists()):
            raise serializers.ValidationError('Рецепт уже добавлен!')
        return data

    def create(self, validated_data):
        favorite = FavoriteRecipe.objects.create(**validated_data)
        favorite.save()
        return favorite


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    id = serializers.CharField(
        read_only=True,
        source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name',
    )

    class Meta:
        model = ShoppingList
        fields = ['id',
                  'cooking_time',
                  'name',
                  'image']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже есть в Вашем списке.'
            )
        ]


class ShoppingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""

    class Meta:
        model = ShoppingList
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже есть в Вашем списке.'
            )
        ]
