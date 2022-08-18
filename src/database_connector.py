import os
import logging
import pymongo


class Database(object):
    URI = (
        "mongodb://"
        + str(os.getenv('MONGO_USERNAME'))
        + ":"
        + str(os.getenv('MONGO_PASSWORD'))
        + "@mongodb:27017/"
    )
    DATABASE = None

    @staticmethod
    def initialize():
        print(Database.URI)
        try:
            client = pymongo.MongoClient(Database.URI, serverSelectionTimeoutMS=5000)
        except Exception as e:
            print("Cannot connect to DB")
            raise e
        else:
            Database.DATABASE = client["freelancers_union"]
            logging.info("Database Initialized")

    @staticmethod
    def insert_one(collection, data):
        Database.DATABASE[collection].insert_one(data)

    @staticmethod
    def insert_many(collection, data):
        Database.DATABASE[collection].insert_many(data)

    @staticmethod
    def update_one(collection, query, data):
        Database.DATABASE[collection].update_one(query, data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
