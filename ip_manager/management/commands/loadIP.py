import json
from django.core.management.base import BaseCommand
from ip_manager.models import IPTable  # Replace with your model

class Command(BaseCommand):
    help = 'Load IP from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        json_file_path = options['json_file']

        with open(json_file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            IPTable.objects.create(
                ip=item['ip'],
                status=item['status'],
            )

        print(self.style.SUCCESS('Data loaded successfully'))
