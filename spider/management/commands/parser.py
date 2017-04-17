from django.core.management.base import BaseCommand
from services.parser import Parser


class Command(BaseCommand):

    def handle(self, *args, **options):
        Parser.pull_offers()
