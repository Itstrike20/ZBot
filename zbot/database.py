import os

import pymongo
from pymongo.errors import ConnectionFailure

from . import logger


class MongoDBConnector:

    USER_NAME = 'Zedd7'
    DATABASE_NAME = 'zbot'
    RECRUITMENT_ANNOUNCES_COLLECTION = 'recruitment_announce'
    PENDING_LOTTERIES_COLLECTION = 'pending_lottery'
    COLLECTION_NAMES = [RECRUITMENT_ANNOUNCES_COLLECTION, PENDING_LOTTERIES_COLLECTION]

    def __init__(self):
        self.client = None
        self.connected = False
        self.database = None
        self.collections = {}

    def open_connection(self):
        try:
            password = os.getenv('MONGODB_PASSWORD')
            if not password:
                raise ConnectionFailure("No MongoDB password found in .env file under the key 'MONGODB_PASSWORD'.")

            self.client = pymongo.MongoClient(f'mongodb+srv://{self.USER_NAME}:{password}@zbot-5waud.gcp.mongodb.net/test?retryWrites=true')
            self.client.admin.command('ismaster')  # Check if connected and raises ConnectionFailure if not
            logger.info(f"Connected to MongoDB database '{self.DATABASE_NAME}'.")
            self.connected = True

            self.database = self.client[self.DATABASE_NAME]
            for collection_name in self.COLLECTION_NAMES:
                self.collections[collection_name] = self.database[collection_name]
            logger.info(f"Loaded {len(self.collections)} collection(s).")

        except ConnectionFailure:
            logger.error(f"Could not connect to MongoDB database '{self.DATABASE_NAME}'.", exc_info=True)

        return self.connected

    # Admin

    def update_recruitment_announces(self, recruitment_announces):
        for announce in recruitment_announces:
            self.database[self.RECRUITMENT_ANNOUNCES_COLLECTION].update_one(
                {'_id': announce.author.id}, {'$set': {'time': announce.create_date}})

    # Lottery

    def update_lottery(self, job_id, data):
        self.database[self.PENDING_LOTTERIES_COLLECTION].update_one({'_id': job_id}, {'$set': data})

    def delete_lottery(self, job_id):
        self.database[self.PENDING_LOTTERIES_COLLECTION].delete_one({'_id': job_id})

    def load_pending_lotteries(self, pending_lotteries):
        data_keys = [
            '_id', 'lottery_id', 'message_id', 'channel_id', 'emoji_code',
            'nb_winners', 'next_run_time', 'organizer_id'
        ]
        for pending_lottery in self.database[self.PENDING_LOTTERIES_COLLECTION].find(
                {}, dict.fromkeys(data_keys, 1)):
            pending_lotteries[pending_lottery['message_id']] = dict(pending_lottery)
