#!/usr/bin/env python3

import logging
import pika

class StorageReplica:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        # Leader -> Replica
        self.channel.exchange_declare(exchange='leader-storage', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        self.leader_queue = result.method.queue
        self.channel.queue_bind(exchange='leader-storage', queue=self.leader_queue)

    def run(self):
        self.channel.basic_consume(queue=self.leader_queue, on_message_callback=self.persist)
        self.channel.start_consuming()

    def persist(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        print(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
