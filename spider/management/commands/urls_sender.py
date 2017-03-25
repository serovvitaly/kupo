from django.core.management.base import BaseCommand
import pika
from offers.models import Offer


class Command(BaseCommand):

    def pull_urls(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='urls', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='urls',
                              body='pull_urls')
        connection.close()

    def pull_offers(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='offers', durable=True)

        for offer in Offer.objects.filter(status__exact='o').all():
            channel.basic_publish(exchange='',
                                  routing_key='offers',
                                  body=str(offer.id))
        connection.close()

    def handle(self, *args, **options):
        self.pull_offers()
