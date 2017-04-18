from django.core.management.base import BaseCommand
from spider.models import *
from services.repository import *
import sys, traceback


class Command(BaseCommand):

    def handle(self, *args, **options):
        base_urls = OfferUrl.objects.all()
        for base_url in base_urls:
            urls = Parser.get_provider_urls(
                base_url.offer_provider.provider,
                base_url.url
            )
            for entry_url in urls:
                entry_url = base_url.url + entry_url
                provider = Parser(base_url.offer_provider.provider)
                offers_urls = provider.get_offers_urls(entry_url)
                if len(offers_urls) < 1:
                    continue
                for offer_url in offers_urls:
                    try:
                        offer_url = base_url.url + offer_url
                        print(offer_url)
                        offer_content = provider.get_content_by_url(offer_url)
                        content_provider = provider.get_content_provider(base_url.offer_provider.provider)
                        offer_entity = content_provider.get_offer_structure(offer_content, offer_url)
                        sql_repository = SqlOfferRepository()
                        sql_repository.add(offer_entity)
                    except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        print('ERROR:', e.__str__())
                        #traceback.print_exception(exc_type, exc_value, exc_traceback)
