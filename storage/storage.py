#!/usr/bin/env python3

import os
import logging
import pika
from multiprocessing import Process
from storage_leader import StorageLeader
from storage_replica import StorageReplica

class Storage:
    def __init__(self, role):
        if role == 'leader':
            self.role = StorageLeader()
        elif role == 'replica':
            self.role = StorageReplica()
        else:
            logging.error('Role %s does not exist' % role)
            return

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        # WD - Storage
        self.channel.exchange_declare(exchange='wd-storage', exchange_type='fanout')
        result = self.channel.queue_declare(queue='wd-storage', durable=True)
        self.wd_queue = result.method.queue
        self.channel.queue_bind(exchange='wd-storage', queue=self.wd_queue)

    def run(self):
        self.process = Process(target=self.role.run)
        self.process.start()

        # Delete auto_ack
        self.channel.basic_consume(queue=self.wd_queue, on_message_callback=self.change_role, auto_ack=True)
        self.channel.start_consuming()

    def change_role(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        role = body.decode()
        if role == 'leader':
            self.role = StorageLeader()
        elif role == 'replica':
            self.role = StorageReplica()
        else:
            logging.error('Role %s does not exist' % role)
            return
        self.process.terminate()
        self.process = Process(target=self.role.run)
        self.process.start()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    role = os.environ['ROLE']
    storage = Storage(role)
    storage.run()
