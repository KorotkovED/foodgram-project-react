from rest_framework import serializers
from .models import (Ingredients,
                     Tags,
                     IngredientsInRecipe,
                     Recipe,
                     FavoriteRecipe,
                     ShoppingList)

# from users.models import User
from rest_framework.exceptions import ValidationError
from drf_base64.fields import Base64ImageField
from django.db.models import F
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

    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredients.measurement_unit')
    amount = serializers.ReadOnlyField(source='ingredients.amount')

    class Meta:
        model = IngredientsInRecipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tag = TagsSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_list = serializers.SerializerMethodField()
    image = Base64ImageField()
    text = serializers.CharField()

    class Meta:
        model = Recipe
        fields = ['id',
                  'author',
                  'name',
                  'image',
                  'text',
                  'ingredients',
                  'tag',
                  'cooking_time',
                  'is_favorite',
                  'is_in_shopping_list']

    @staticmethod
    def get_ingredients(obj):
        ingredients = Ingredients.objects.filter(recipe=obj)
        return ShowIngredientsInRecipeSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=request.user,
                                             recipe=obj).exists()

    def get_is_in_shopping_list(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=request.user,
                                           recipe=obj).exists()


class AddIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления Ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ['id', 'amount']


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов."""

    name = serializers.CharField(max_length=200)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    ingredients = AddIngredientInRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=1)
    image = Base64ImageField()
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        exclude = ['pub_date']

    def ingredients_validate(self, ingredients):
        if not ingredients:
            raise ValidationError(
                'Выберите игредиенты!'
            )
        ingr_id = [item['id'] for item in ingredients]
        if len(ingr_id) != len(set(ingr_id)):
            raise ValidationError(
                'Неуникальные ингредиенты!'
            )
        return ingredients

    def add_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if IngredientsInRecipe.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists():
                amount += F('amount')
            IngredientsInRecipe.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientsInRecipe.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        response = super(RecipeSerializer, self).to_representation(instance)
        if instance.image:
            response['image'] = instance.image.url
        return response


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
