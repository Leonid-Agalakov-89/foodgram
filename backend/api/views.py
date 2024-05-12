import random
import string
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, CustomUserSerializer,
                             GetRecipeSerializer, IngredientSerializer,
                             RecipeInfoSerializer, RecipeSerializer,
                             ShortLinkSerializer, SubscribeSerializer,
                             TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, ShortLink, Tag)
from users.models import Subscribe


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.sample(characters, k=4))
    return 'http://foodgram89.line.pm/s/' + short_url


class GetRecipeShortLink(APIView):

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        short_url = generate_short_url()
        link_obj, _ = ShortLink.objects.get_or_create(
            original_url=recipe.get_absolute_url(),
            defaults={'short_link': short_url}
        )
        serializer = ShortLinkSerializer(link_obj)
        return Response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для обработки запросов на получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для обработки запросов на получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_400_BAD_REQUEST)
            return self.add_to(Favorite, user=user, recipe=recipe)
        else:
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_404_NOT_FOUND)
            return self.delete_from(Favorite, user=user, recipe=recipe)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_400_BAD_REQUEST)
            return self.add_to(ShoppingCart, user=user, recipe=recipe)
        else:
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_404_NOT_FOUND)
            return self.delete_from(ShoppingCart, user=user, recipe=recipe)

    def add_to(self, model, user, recipe):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeInfoSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, recipe):
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже удален!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%d-%m-%Y}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """ViewSet для модели Пользователя"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def subscribe(self, request, id):
        """Метод для управления подписками """

        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Невозможно подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(author,
                                             context={"request": request})
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Метод для подписки"""

        user = request.user
        follows = User.objects.filter(subscribing__user=user)
        page = self.paginate_queryset(follows)
        serializer = SubscribeSerializer(page,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['GET', 'PUT'],
        permission_classes=[IsAuthenticated],
        detail=False,
        url_path='me/avatar',
        url_name='avatar'
    )
    def change_avatar(self, request):
        """Метод для изменения аватарки пользователя"""

        if 'avatar' not in request.data:
            return Response(['Contact phone field is required.'], status=400)
        avatar = self.request.user
        serializer = AvatarSerializer(avatar, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @change_avatar.mapping.delete
    def delete_avatar(self, request):
        """Метод для удаления аватарки пользователя"""

        avatar = self.request.user
        serializer = AvatarSerializer(avatar, data=request.data)
        if serializer.is_valid():
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
