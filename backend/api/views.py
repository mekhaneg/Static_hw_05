from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from django.db.models import Sum

from recipes import models
from api import serializers
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from backend import settings


class TagView(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permissions = (AllowAny,)
    pagination_class = None


class IngredientsView(viewsets.ModelViewSet):
    queryset = models.Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    search_fields = ('name', )
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    permissions = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        method = self.request.method
        if method == 'POST' or method == 'PATCH':
            return serializers.CreateRecipeSerializer
        return serializers.ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteView(APIView):
    permissions = (IsAuthenticatedOrReadOnly,)

    @action(
        methods=(
            'post',
        ),
        detail=True,
    )
    def post(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        if models.Favorite.objects.filter(
            user=user, recipe__id=recipe_id
        ).exists():
            return Response(
                {'Ошибка': 'Уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = serializers.FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=(
            'DELETE',
        ),
        detail=True,
    )
    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(models.Recipe, id=recipe_id)
        favorite = models.Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    @action(
        methods=(
            'post',
        ),
        detail=True,
    )
    def post(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        if models.ShoppingCart.objects.filter(
                user=user, recipe__id=recipe_id
        ).exists():
            return Response(
                {'Ошибка': 'Уже есть в корзине'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = serializers.ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        method=(
            'delete',
        ),
        detail=True,
    )
    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(models.Recipe, id=recipe_id)
        shoppingcart = models.ShoppingCart.objects.filter(
            user=user, recipe=recipe
        )
        if not shoppingcart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shoppingcart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(('GET',))
def download_shopping_cart(request):
    user = request.user
    if not user.shopping_cart.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ingredients = models.IngredientInRecipe.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(sum_amount=Sum('amount'))

    wishlist = []
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        amount = ingredient['sum_amount']
        measurement_unit = ingredient['ingredient__measurement_unit']
        wishlist.append(
            f"{name} - {amount} {measurement_unit}"
        )
    response = HttpResponse(
        wishlist, content_type=settings.CONTENT_TYPE_CONST
    )
    return response
