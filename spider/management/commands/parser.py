from django.core.management.base import BaseCommand
from services.repository import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        html_repository = HtmlOfferRepository('kupibonus')
        offer_entity = html_repository.get_by_url(
            'http://www.kupibonus.ru/actions/spa/den-razvlecheniy-v-akvap/'
        )
        sql_repository = SqlOfferRepository()
        sql_repository.add(offer_entity)
