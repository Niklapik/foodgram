from rest_framework import serializers

from rest_framework.exceptions import NotAuthenticated

from recipes.models import Tag, Ingredient, FavoriteRecipe, Recipe, User, RecipeIngredient
from users.models import Subscription, CustomUser
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer

import base64

from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


# class FavoriteRecipeSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='recipe.name', read_only=True)
#     cooking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)
#     image = serializers.ImageField(source='recipe.image', read_only=True)
#
#     class Meta:
#         model = Recipe
#         fields = ['id', 'name', 'image', 'cooking_time']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar')

    class Meta:
        model = Subscription
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar']

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.subscriptions.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class UserCreateSerializer(DjoserUserCreateSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False

    def to_representation(self, instance):
        if not isinstance(instance, User):
            raise NotAuthenticated('Необходимо авторизоваться.')
        return super().to_representation(instance)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer(read_only=True)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле ingredients не может быть пустым",
                code='empty_ingredients'
            )

        # Проверка на дубликаты ингредиентов
        ingredient_ids = [item['ingredient'].id for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться",
                code='duplicate_ingredients'
            )

        # Проверка количества ингредиентов
        for item in value:
            if item['amount'] < 1:
                raise serializers.ValidationError(
                    f"Количество ингредиента {item['ingredient'].name} должно быть не меньше 1",
                    code='invalid_amount'
                )

        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле tags не может быть пустым",
                code='empty_tags'
            )

        # Проверка на дубликаты тегов
        if len(value) != len(set(tag.id for tag in value)):
            raise serializers.ValidationError(
                "Теги не должны повторяться",
                code='duplicate_tags'
            )

        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не меньше 1 минуты",
                code='invalid_cooking_time'
            )
        return value

    def validate(self, data):
        # Общая валидация
        if 'recipe_ingredients' not in data or not data['recipe_ingredients']:
            raise serializers.ValidationError(
                {"ingredients": "Необходимо указать хотя бы один ингредиент"},
                code='missing_ingredients'
            )

        if 'tags' not in data or not data['tags']:
            raise serializers.ValidationError(
                {"tags": "Необходимо указать хотя бы один тег"},
                code='missing_tags'
            )

        return data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'image',
                  'name', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.in_shopping_carts.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return representation

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.in_shopping_carts.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return representation


class PostFavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
