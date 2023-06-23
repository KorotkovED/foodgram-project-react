from rest_framework import viewsets, status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter, IngredientFilter
from .models import (Recipe,
                     Tags,
                     Ingredients,
                     ShoppingList,
                     FavoriteRecipe,
                     IngredientsInRecipe)
from .serializers import (RecipeSerializer,
                          TagsSerializer,
                          IngredientsSerializer,
                          RecipeCreateSerializer,
                          FavoriteRecipeSerializer,
                          FavoriteCreateSerializer,
                          ShoppingCreateSerializer
                          )
from .permissions import (IsAuthorOrAdmin,
                          IsAdminOrReadOnly,
                          IsAuthorOrAdminOnlyPermission)
from users.pagination import LimitPageNumerPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from django.db.models import F, Sum
from django.http import HttpResponse


def custom_post_delete(self, request, pk, func_model):
    """Функция-обработчик POST, DELETE запросов """
    user = self.request.user
    recipe = self.get_object()
    if request.method == 'DELETE':
        instance = func_model.objects.filter(recipe=recipe, user=user)
        if not instance:
            raise serializers.ValidationError(
                {
                    'errors': [
                        'Этот рецепт в списке отсутствует.'
                    ]
                }
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = {
        'user': user.id,
        'recipe': pk
    }
    favorite = self.get_serializer(data=data)
    favorite.is_valid(raise_exception=True)
    favorite.save()
    serializer = FavoriteRecipeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = LimitPageNumerPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        if self.action == 'favorite':
            return FavoriteCreateSerializer
        if self.action == 'shopping_cart':
            return ShoppingCreateSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (permissions.AllowAny,)
        elif self.action in ('favorite', 'shopping_cart'):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.request.method in (
            'PATCH', 'DELETE'
        ):
            self.permission_classes = (IsAuthorOrAdminOnlyPermission,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'], detail=True,
    )
    def favorite(self, request, pk):
        func_model = FavoriteRecipe
        return custom_post_delete(self, request, pk, func_model)

    @action(
        methods=['POST', 'DELETE'], detail=True,
    )
    def shopping_cart(self, request, pk):
        func_model = ShoppingList
        return custom_post_delete(self, request, pk, func_model)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        methods=['GET'],
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__buyer__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'Shopping_cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для обработки тэгов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для обработки ингредиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
