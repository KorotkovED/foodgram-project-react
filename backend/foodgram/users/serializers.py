from .models import User, Subscribtion
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers, validators
from recipe.serializers import RecipeSerializer


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


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        fields = ['email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password']


class SubscribtionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_sub = serializers.SerializerMethodField(read_only=True)
    recipe = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['email',
                  'username',
                  'id',
                  'first_name',
                  'last_name',
                  'is_sub',
                  'recipe',
                  'recipes_count']

    def get_is_sub(self, obj):
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
        serializer = serializers.ListSerializer(child=RecipeSerializer())
        return serializer.to_representation(recipes)

    def get_recipes_count(obj):
        return obj.recipes.count()
