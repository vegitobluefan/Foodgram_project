from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse

from recipes.models import Recipe, ShoppingCart, IngredientRecipe


def post_method(request, instance, serializer_class):
    serializer = serializer_class(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_method(request, instance, model):
    if not model.objects.filter(
        user=request.user, recipe=instance
    ).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    model.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def pdf_file(user):
    ingredient_list = []
    ingredient_dict = {}
    shopping_cart = ShoppingCart.objects.filter(user=user)

    for needed_recipe in shopping_cart:
        recipe = Recipe.objects.get(id=needed_recipe.recipe.id)
        ingredients = IngredientRecipe.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            ingredient_dict[
                f'{ingredient.ingredient.name}'
                f'({ingredient.ingredient.measurement_unit})'
            ] = ingredient.amount + ingredient_dict.setdefault(
                f'{ingredient.ingredient.name}'
                f'({ingredient.ingredient.measurement_unit})', 0
            )
    for key, value in ingredient_dict.items():
        ingredient_list.append(f'{key} - {value}\n')
    response = HttpResponse(ingredient_list, content_type='text/plain')
    response['Content-Disposition'] = 'attachment'
    return response
