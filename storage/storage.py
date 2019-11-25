#!/usr/bin/env python3

import os
import logging
import pika
from multiprocessing import Process
from storage_leader import StorageLeader
from storage_replica import StorageReplica

ROLES = {'leader': StorageLeader(), 'replica': StorageReplica()}

class Storage:
    def __init__(self, role):
        if not role in ROLES:
            logging.ERROR('Role %s does not exist' % role)
            return
        self.role = ROLES[role]

    def run(self):
        self.role.run()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    role = os.environ['ROLE']
    storage = Storage(role)
    storage.run()
