import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            'data/ingredients.csv', 'r', encoding='utf-8'
        ) as f:
            reader = csv.reader(f, delimiter=',')
            ingredients = []
            for row in reader:
                name, measurement_unit = row
                if name:
                    ingredient = Ingredient(
                        name=name, measurement_unit=measurement_unit
                    )
                    ingredients.append(ingredient)
            Ingredient.objects.bulk_create(ingredients)
