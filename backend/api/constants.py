NAME_MAX_LENGTH = 80
SLUG_MAX_LENGTH = 50
UNIT_MAX_LENGTH = 20

LIMIT_COOKING_TIME = 1
LIMIT_INGREDIENTS = 1

LIMIT_COOKING_MESSAGE = (f'Минимальное время '
                         f'приготовления: {LIMIT_COOKING_TIME} минута!')
LIMIT_INGREDIENTS_MESSAGE = (f'Минимальное '
                             f'количество ингредиентов: {LIMIT_INGREDIENTS}!')

RECIPE_NO_INGREDIENTS_MESSAGE = (
    'Рецепт не может быть без ингредиентов. '
    'Добавьте хотя бы один ингредиент.'
)
