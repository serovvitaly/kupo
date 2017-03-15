from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Parsing...')
        from services.biglion import Provider
        offers = Provider().all()
        print(offers)
        pass
