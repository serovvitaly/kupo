from django.core.management.base import BaseCommand
from spider.models import *
from services.repository import *
import sys, traceback
from pymongo import MongoClient
from datetime import datetime

client = MongoClient()
db = client.log
prs = db.parser


class Command(BaseCommand):

    def handle(self, *args, **options):

        sql_repository = SqlOfferRepository()
        base_urls = OfferUrl.objects.all()
        for base_url in base_urls:
            urls = Parser.get_provider_urls(
                base_url.offer_provider.provider,
                base_url.url
            )
            for entry_url in urls:
                entry_url = base_url.url + entry_url
                provider = Parser(base_url.offer_provider.provider)
                html_repository = HtmlOfferRepository(base_url.offer_provider.provider)
                offers_urls = provider.get_offers_urls(entry_url)
                if len(offers_urls) < 1:
                    continue
                for offer_url in offers_urls:
                    try:
                        offer_url = base_url.url + offer_url
                        print(offer_url)
                        offer_entity = html_repository.get_by_url(offer_url)
                        sql_repository.add(offer_entity)
                    except Exception as e:
                        # exc_type, exc_value, exc_traceback = sys.exc_info()
                        # traceback.print_exception(exc_type, exc_value, exc_traceback)
                        print('ERROR:', e.__str__())
                        prs.insert_one({
                            'url': offer_url,
                            'type': 'error',
                            'message': e.__str__(),
                            'created_at': datetime.now(),
                        })
