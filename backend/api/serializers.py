from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ValidationError

from api_users.serializers import CustomUserSerializer
from recipes import models
from backend import settings


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        model = models.Recipe
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
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = models.IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        user = request.user
        return models.Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        user = request.user
        return models.ShoppingCart.objects.filter(
            recipe=obj, user=user
        ).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all()
    )

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(
        many=True, queryset=models.Tag.objects.all(), slug_field='id'
    )

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, data):
        if data < settings.MIN_COOKING_TIME:
            raise serializers.ValidationError(
                f'Введите не меньше {settings.MIN_COOKING_TIME} для времени'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = models.Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients_data:
            ingredient_model = ingredient['id']
            amount = ingredient['amount']
            if settings.MIN_AMOUNT_VALUE > amount:
                raise ValidationError(
                    f'Введите >= {settings.MIN_AMOUNT_VALUE} для Ингредиента'
                )
            if models.IngredientInRecipe.objects.filter(
                ingredient=ingredient_model, recipe=recipe
            ).exists():
                iir = models.IngredientInRecipe.objects.get(
                    ingredient=ingredient_model, recipe=recipe
                )
                iir.amount = iir.amount + amount
                iir.save(update_fields=['amount'])
            else:
                models.IngredientInRecipe.objects.create(
                    ingredient=ingredient_model, recipe=recipe, amount=amount
                )
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        models.TagsInRecipe.objects.filter(recipe=instance).delete()
        models.IngredientInRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            ingredient_model = ingredient['id']
            amount = ingredient['amount']
            if settings.MIN_AMOUNT_VALUE > amount:
                raise ValidationError(
                    f'Введите >= {settings.MIN_AMOUNT_VALUE} для Ингредиента'
                )
            if models.IngredientInRecipe.objects.filter(
                ingredient=ingredient_model, recipe=instance
            ).exists():
                iir = models.IngredientInRecipe.objects.get(
                    ingredient=ingredient_model, recipe=instance
                )
                iir.amount = iir.amount + amount
                iir.save(update_fields=['amount'])
            else:
                models.IngredientInRecipe.objects.create(
                    ingredient=ingredient_model, recipe=instance, amount=amount
                )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.tags.set(tags_data)
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=models.Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all()
    )

    class Meta:
        model = models.Favorite
        fields = ('recipe', 'user')


class ShoppingCartSerializer(FavoriteSerializer):
    class Meta:
        model = models.ShoppingCart
        fields = ('recipe', 'user')
