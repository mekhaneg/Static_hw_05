from django.contrib import admin
from recipes import models

admin.site.register(models.TagsInRecipe)
admin.site.register(models.IngredientInRecipe)


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
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
        'name', 'author__username'
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


@admin.register(models.ShoppingCart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'recipe'
    )
    search_fields = (
        'user__username', 'recipe__name'
    )
