from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import urllib.request
import re
from zalipay.models import Post as PostDocument

from datetime import datetime


class Command(BaseCommand):

    @staticmethod
    def get_content_by_url(url):
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            content = f.read()
            return content.decode('utf8')

    def handle(self, *args, **options):
        tags = {
            'development': 'Развитие личности',
            'relations': 'Любовь и отношения',
            'communication': 'Психология общения',
            'chsv': 'Уверенность в себе',
            'meditation': 'Осознанность',
            'psychic': 'Психика и восприятие',
            'efficiency': 'Продуктивность',
            'life': 'Философия жизни',
            'way': 'Духовный путь',
            'tales': 'Абстракции',
            'health': 'Здоровье',
        }
        sections_urls = [
            'http://progressman.ru/development/',
            'http://progressman.ru/relations/',
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
            myli = str(soup.find('div', 'post-bodycopy').find('ul'))
            urls = re.findall(r'<a href="([^"]+)">[^<]+</a>', myli)
            tag = re.findall(r'\/(\w+)\/$', section_url)[0]
            tag_ru = tags[tag]
            for post_url in urls:
                post_html = self.get_content_by_url(post_url)
                post_soup = BeautifulSoup(post_html, 'html.parser')
                post_html = post_soup.find('div', 'post')
                title = post_html.find('h1').text
                content = str(post_html.find('div', 'post-bodycopy'))
                post = PostDocument(
                    title=title,
                    content=content,
                    meta_data={'tag': tag, 'tag_ru': tag_ru, 'source_url': post_url},
                    ribbon_id=2
                )
                post.save()
