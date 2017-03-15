from django.core.management.base import BaseCommand
from pymongo import MongoClient
from services.biglion import Provider


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Parsing...')
        client = MongoClient('localhost', 27017)
        db = client['kupon']
        offers = Provider().all()
        col_offers = db.offers
        for offer in offers:
            col_offers.insert_one(offer.__dict__)
