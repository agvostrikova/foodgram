"""Загрузка информации."""

import csv

from django.core.management import BaseCommand

from foodgram_backend import settings
from recipes.models import Ingredient, Tag


MODELS_FILES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv'
}

TABLE_COLUMN = {
    'ingredients.csv': ['name', 'measurement_unit'],
    'tags.csv': ['name', 'slug'],
}

class Command(BaseCommand):
    """Импорт файлов csv."""

    def handle(self, *args, **options):
        """Загрузка рецептов, тегов."""
        for model, file in MODELS_FILES.items():
            all_count = model.objects.count()
            reader = csv.DictReader(
                open(
                    f'{settings.BASE_DIR}/data/{file}', 'r', encoding='utf-8'
                ), fieldnames=TABLE_COLUMN[file]
            )
            model.objects.bulk_create(model(**data) for data in reader)

            if model.objects.count() > all_count:
                self.stdout.write(
                    self.style.SUCCESS(f'Загрузка данных {file} завершена!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при загрузке {file}!')
                )

        self.stdout.write(self.style.SUCCESS(
            '=== Ингредиенты и теги успешно загружены ===')
        )
