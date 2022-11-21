import os
import logging
import pymongo


class Database(object):
    port = ":" + str(os.getenv("MONGO_PORT")) if os.getenv("MONGO_PORT") else ""
    URI = (
            "mongodb://"
            + str(os.getenv('MONGO_USERNAME'))
            + ":"
            + str(os.getenv('MONGO_PASSWORD'))
            + "@" + str(os.getenv('MONGO_ADDRESS'))
            + str(port) + "/"
    )
    DATABASE: pymongo.mongo_client.database.Database = None

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
    def init_timeseries_db(collection_name: str, collection_options: dict) -> pymongo.collection.Collection:
        """
        Get or create a timeseries collection in database.
        If the timeseries exists, it oly makes sure that it's timeseries collection and nothing more
        Parameters
        ----------
        collection_name: name of collection that will be used
        collection_options: set of options this collection should have

        Returns
        -------
            the timeseries collection with such name (and hopefully those options)
        """
        current_collection_options = Database.DATABASE[collection_name].options()

        if collection_name not in Database.DATABASE.list_collection_names():
            Database.DATABASE.create_collection(name=collection_name, timeseries=collection_options,
                                 expireAfterSeconds=94608000)
        elif "timeseries" not in current_collection_options.keys():
            raise Exception(f"collection {collection_name} exists, but isn't timeseries")
        collection: pymongo.collection.Collection = Database.DATABASE[collection_name]
        return Database.DATABASE[collection_name]

    @staticmethod
    def init_collection(collection_name: str, collection_options: dict) -> pymongo.collection.Collection:
        """
        Get or create a collection in database.
        If the collection exists, do nothing.
        Parameters
        ----------
        collection_name: name of collection that will be used
        collection_options: set of options this collection should have

        Returns
        -------
            the collection name.
        """
        current_collection_options = Database.DATABASE[collection_name].options()

        if collection_name not in Database.DATABASE.list_collection_names():
            Database.DATABASE.create_collection(name=collection_name)
        elif "timeseries"in current_collection_options.keys():
            raise Exception(f"collection {collection_name} exists, but is a timeseries")
        collection: pymongo.collection.Collection = Database.DATABASE[collection_name]
        return Database.DATABASE[collection_name]

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
