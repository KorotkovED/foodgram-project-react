from django.contrib import admin
from .forms import TagForm
from .models import (FavoriteRecipe, Ingredients, Recipe, IngredientsInRecipe,
                     ShoppingList, Tags)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    form = TagForm
    search_fields = ('name',)
    ordering = ('color',)


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'units',
        'get_recipes_count',
    )
    search_fields = ('name',)
    ordering = ('units',)

    def get_recipes_count(self, obj):
        return IngredientsInRecipe.objects.filter(ingredient=obj.id).count()


class RecipeIngredientsInline(admin.TabularInline):
    model = IngredientsInRecipe
    min_num = 1
    extra = 1


@admin.register(IngredientsInRecipe)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    list_filter = ('id', 'recipe', 'ingredient')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'in_favorite',
    )
    list_filter = ('name', 'author',)
    readonly_fields = ('in_favorite',)
    inlines = (RecipeIngredientsInline,)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
