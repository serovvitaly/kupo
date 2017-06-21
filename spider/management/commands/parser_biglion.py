from django.core.management.base import BaseCommand
from spider.models import *
from pymongo import MongoClient
from datetime import datetime
from services.repository import *
from services.parser import Parser
from services.provider.biglion import ContentDispatcher

client = MongoClient()
db = client.biglion


class Command(BaseCommand):

    def handle(self, *args, **options):

        base_urls = OfferUrl.objects.filter(is_supervised__exact=False).all()

        for base_url in base_urls:

            html_repository = HtmlOfferRepository(base_url.offer_provider.provider)

            provider = Parser(base_url.offer_provider.provider)

            pages_count = provider.get_pages_count(base_url.url)

            for page in range(1, pages_count+1):

                list_url = base_url.url + '?page=' + str(page)
                print(list_url)

                offers_urls = provider.get_offers_urls(list_url)
                if len(offers_urls) < 1:
                    continue

                for offer_url in offers_urls:
                    print(' -', offer_url)
                    offer_content = provider.get_content_by_url(offer_url)

                    offer_content_disp = ContentDispatcher(offer_content)

                    offer_items = offer_content_disp.get_items()

                    for offer_item in offer_items:
                        data = offer_item.__dict__
                        data['offer_url'] = offer_url
                        data['created_at'] = datetime.now()
                        db.offers_items.insert_one(data)


