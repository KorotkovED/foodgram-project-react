from django.http import HttpResponse
from .models import ShoppingList


def get_shopping_list(request):
    shopping_cart = ShoppingList.objects.filter(user=request.user).all()
    shopping_list = {}
    for item in shopping_cart:
        for recipe_ingredient in item.recipe.iir.all():
            name = recipe_ingredient.ingredient.name
            units = recipe_ingredient.ingredient.units
            amount = recipe_ingredient.amount
            if name not in shopping_list:
                shopping_list[name] = {
                    'name': name,
                    'units': units,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
    content = (
        [f'{item["name"]} ({item["units"]}) '
         f'- {item["amount"]}\n'
         for item in shopping_list.values()]
    )
    filename = 'shopping_list.txt'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(filename)
    )
    return response