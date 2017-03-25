from django.core.management.base import BaseCommand
from services.parser import Parser
import pika
from offers.models import Offer


class Command(BaseCommand):

    @staticmethod
    def go(ch, method, properties, body):
        offer_id = body.decode('utf8')
        parser = Parser()
        parser.pull_offer_by_id(offer_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='offers', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.go, queue='offers')
        channel.start_consuming()
