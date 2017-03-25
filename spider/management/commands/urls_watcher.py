from django.core.management.base import BaseCommand
from services.parser import Parser
import pika


class Command(BaseCommand):

    @staticmethod
    def go(ch, method, properties, body):
        cmd = body.decode('utf8')
        if False:
            pass
        elif cmd == 'pull_urls':
            parser = Parser()
            parser.pull_urls()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='urls', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.go, queue='urls')
        channel.start_consuming()
