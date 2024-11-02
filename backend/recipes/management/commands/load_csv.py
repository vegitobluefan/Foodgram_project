import csv

from django.core.management.base import BaseCommand
from foodgram.settings import CSV_PATH
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            f'{CSV_PATH}\\ingredients.csv', 'r',
            encoding="utf-8"
        ) as file:
            reader = csv.reader(file, delimiter=',')
            ingredients_to_create = []
            for row in reader:
                name, unit = row
                if name:
                    ingredient = Ingredient(name=name, measurement_unit=unit)
                    ingredients_to_create.append(ingredient)
            Ingredient.objects.bulk_create(ingredients_to_create)
