from .models import User, Subscribtion
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators
from recipe.models import Recipe
from rest_framework.validators import UniqueTogetherValidator


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = ['email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password']


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя на автора."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(user=self.context['request'].user,
                                           author=obj).exists()


class SubscribtionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['email',
                  'username',
                  'id',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count']

    def get_is_subscribed(self, obj):
        """Проверка подписки на автора."""
        user = self.context.get('request').user
        if not user:
            return False
        return Subscribtion.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = (
            obj.recipes.all()[:int(recipes_limit)]
            if recipes_limit else obj.recipes
        )
        return FavoriteShoppingSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для сериализации рецептов, находящися в списке
    избранного и списке покупок.
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на автора."""

    class Meta:
        model = Subscribtion
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.')
        return data
