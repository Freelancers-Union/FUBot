import os
from pymongo import MongoClient


def get_database():
    """Creates connection to MongoDB.

    Returns
    ------
    client : pymongo client
    """
    CONNECTION_STRING = (
        "mongodb://"
        + str(os.getenv("MONGO_USERNAME"))
        + ":"
        + str(os.getenv("MONGO_PASSWORD"))
        + "@localhost:27017/"
    )
    try:
        client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=5000)
    except Exception as e:
        raise e
    else:
        return client["freelancers_union"]


if __name__ == "__main__":

    # Get the database
    dbname = get_database()
    collection_name = dbname["members"]
