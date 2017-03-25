from django.core.management.base import BaseCommand
import pika


class Command(BaseCommand):

    def handle(self, *args, **options):
        provider_name = input('Enter provider name: ')
        print('Pull offers for', provider_name)

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='helloName')

        channel.basic_publish(exchange='',
                              routing_key='helloName',
                              body='Hello World!')

        connection.close()
