from csv import reader
from django.core.management.base import BaseCommand
from recipe.models import Ingredients


class Command(BaseCommand):
    """Создает записи в модели Ingredients из списка."""
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipe/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredients.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
