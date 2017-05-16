from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import urllib.request
import re

from datetime import datetime


class Command(BaseCommand):

    @staticmethod
    def get_content_by_url(url):
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            content = f.read()
            return content.decode('utf8')

    def handle(self, *args, **options):

        sections_urls = [
            'http://progressman.ru/development/',
            'http://progressman.ru/relations',
            'http://progressman.ru/communication/',
            'http://progressman.ru/chsv/',
            'http://progressman.ru/meditation/',
            'http://progressman.ru/psychic/',
            'http://progressman.ru/efficiency/',
            'http://progressman.ru/life/',
            'http://progressman.ru/way/',
            'http://progressman.ru/tales/',
            'http://progressman.ru/health/',
        ]



        for section_url in sections_urls:
            print(section_url)
            html = self.get_content_by_url(section_url)
            soup = BeautifulSoup(html, 'html.parser')
            myli = str(soup.find('div', 'myli'))

            print(str(myli))
