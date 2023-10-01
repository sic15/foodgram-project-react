import csv
import pathlib

from django.core.management.base import BaseCommand

from food.models import Ingredient


class Command(BaseCommand):
    help = 'load csv files to sql database'

    def handle(self, *args, **options):
        category_path = pathlib.Path("food/data/ingredients.csv")
        with open(category_path.absolute(),
                  encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                name, measurement_unit = row
               # name = row['name']
               # measurement_unit = row['measurement_unit']
                ingredient = Ingredient( name=name, measurement_unit=measurement_unit)
                ingredient.save()
