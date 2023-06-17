from rest_framework import viewsets, status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from .models import (Recipe,
                     Tags,
                     Ingredients)
from .serializers import (AddRecipeSerializer,
                          RecipeSerializer,
                          TagsSerializer,
                          IngredientsSerializer
                          )
from .permissions import IsAuthorOrAdmin, IsAdminOrReadOnly
from users.pagination import LimitPageNumerPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from .utils import get_shopping_list


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = AddRecipeSerializer
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = LimitPageNumerPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action,
                                           self.serializer_class)

    def _favorite_shopping_post_delete(self, related_manager):
        recipe = self.get_object()
        if self.request.method == 'DELETE':
            related_manager.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if related_manager.filter(recipe=recipe).exists():
            raise ValidationError('Рецепт уже в избранном')
        related_manager.create(recipe=recipe)
        serializer = RecipeSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def favorite(self, request, pk=None):
        return self._favorite_shopping_post_delete(
            request.user.favorite
        )

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def shopping_cart(self, request, pk=None):
        return self._favorite_shopping_post_delete(
            request.user.shopping_user
        )

    @action(
            detail=True,
            methods=['GET'],
            url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        try:
            return get_shopping_list(request)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для обработки тэгов.
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для обработки ингредиентов.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
