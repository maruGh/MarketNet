from typing import Any
from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Command to populate the database with products and collections.'

    def handle(self, *args: Any, **options: Any) -> str | None:
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'seed.sql')
        sql = Path(file_path).read_text()

        with connection.cursor() as cursor:
            try:
                print('Running SQL query ...')
                cursor.execute(sql)
                print('Done running SQL query')
            except Exception as e:
                print(e)
