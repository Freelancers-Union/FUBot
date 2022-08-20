import os
import logging
import pymongo


class Database(object):
    URI = (
        "mongodb://"
        + str(os.getenv("MONGO_USERNAME"))
        + ":"
        + str(os.getenv("MONGO_PASSWORD"))
        + "@"
        + str(os.getenv("MONGO_ADDRESS"))
        + ":27017/"
    )
    DATABASE = None

    @staticmethod
    def initialize():
        print(Database.URI)
        try:
            client = pymongo.MongoClient(Database.URI, serverSelectionTimeoutMS=5000)
            Database.DATABASE = client["freelancers_union"]
            print(client.list_database_names())
        except pymongo.errors.ServerSelectionTimeoutError:
            logging.exception("DB server connection timed out.")
        else:
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
