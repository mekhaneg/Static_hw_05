from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from backend import settings

User = get_user_model()


class Tag(models.Model):

    BLUE = '#0000FF'
    RED = '#FF0000'
    PURPLE = '#800080'
    GREEN = '#008000'
    YELLOW = '#FFFF00'

    COLOR_CHOICES = (
        (BLUE, 'Синий'),
        (RED, 'Красный'),
        (PURPLE, 'Фиолетовый'),
        (GREEN, 'Зелёный'),
        (YELLOW, 'Жёлтый'),
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
        help_text='Название тега'
    )
    color = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        unique=True,
        verbose_name='Цвет',
        help_text='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
        help_text='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        help_text='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор'
    )
    tags = models.ManyToManyField(
        Tag, through='TagsInRecipe',
        related_name='recipes',
        verbose_name='Тег',
        help_text='Тег'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления',
        validators=(MinValueValidator(settings.MIN_COOKING_TIME),)
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        blank=True,
        verbose_name='Ингредиенты',
        help_text='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации',
        help_text='Время публикации'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Изображение'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagsInRecipe(models.Model):

    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег в рецепте',
        help_text='Тег в рецепте',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт'
    )

    class Meta:
        verbose_name = 'Теги в рецепте'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.tag} in {self.recipe}'


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        help_text='Ингредиент в рецепте'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        null=True,
        verbose_name='Количество ингредиента',
        help_text='Количество ингредиента',
        validators=(MinValueValidator(settings.MIN_AMOUNT_VALUE),)
    )

    class Meta:
        verbose_name = 'Количетсво ингредиента в рецепте'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Пользователь',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique favorite'),
        )

    def __str__(self):
        return f'{self.user} added in favorite {self.recipe}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Пользователь',
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_cart'),
        )

    def __str__(self):
        return f'{self.user} added in shopping_cart {self.recipe}'
