#!/usr/bin/env python3

import logging
import pika

class StorageLeader:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        # Leader -> Replica
        self.channel.exchange_declare(exchange='leader-replica', exchange_type='fanout')

        # Data -> Leader
        self.channel.exchange_declare(exchange='data', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        self.data_queue = result.method.queue
        self.channel.queue_bind(exchange='data', queue=self.data_queue)

    def run(self):
        # Delete auto_ack
        self.channel.basic_consume(queue=self.data_queue, on_message_callback=self.persist, auto_ack=True)
        self.channel.start_consuming()

    def persist(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        print(body)
        self.channel.basic_publish(exchange='leader-replica', routing_key='', body=body,
                                   properties=pika.BasicProperties(delivery_mode=2,))
