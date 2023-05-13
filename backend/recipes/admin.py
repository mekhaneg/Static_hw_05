from django.contrib import admin
from recipes import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'measurement_unit',
    )


class IngredientsInLine(admin.TabularInline):
    model = models.Recipe.ingredients.through


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        IngredientsInLine,
    )
    fields = (
        ('author'),
        ('name', 'cooking_time',),
        ('text',),
        ('image',),
    )
    search_fields = (
        'name', 'author__username'
    )
    list_filter = (
        'tags',
    )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug'
    )
    search_fields = (
        'name', 'color'
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'recipe'
    )
    search_fields = (
        'user__username', 'recipe__name'
    )
    list_filter = (
        'recipe__tags',
    )


@admin.register(models.ShoppingCart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'recipe'
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )

    list_filter = (
        'recipe__tags',
    )


@admin.register(models.IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient', 'recipe', 'amount',
    )
    search_fields = (
        'recipe__author__email',
        'recipe__author__username',
        'recipe__name',
        'ingredient__name',

    )
    list_filter = (
        'recipe__tags',
    )


@admin.register(models.TagsInRecipe)
class TagsInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe', 'tag'
    )
    search_fields = (
        'recipe__author__email',
        'recipe__author__username',
        'recipe__name'
    )
    list_filter = (
        'tag',
    )
