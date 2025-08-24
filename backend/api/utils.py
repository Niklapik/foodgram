from django.http import HttpResponse


def create_shopping_list(recipes):
    ingredients = {}
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            key = (recipe_ingredient.ingredient.name,
                   recipe_ingredient.ingredient.measurement_unit)
            if key in ingredients:
                ingredients[key] += recipe_ingredient.amount
            else:
                ingredients[key] = recipe_ingredient.amount

    lines = []
    for (name, unit), amount in ingredients.items():
        lines.append(f"{name} - {amount} {unit}")

    text_content = "Список покупок:\n\n" + "\n".join(lines)
    text_content += f"\n\nВсего ингредиентов: {len(ingredients)}"

    response = HttpResponse(text_content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"'
    )
    return response
