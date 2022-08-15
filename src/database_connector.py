import os
from pymongo import MongoClient

def get_database():
    CONNECTION_STRING = "mongodb://"+str(os.getenv('MONGO_USERNAME'))+":"+str(os.getenv('MONGO_PASSWORD'))+"@localhost:27017/"
    client = MongoClient(CONNECTION_STRING)
    return client['freelancers_union']

if __name__ == "__main__":    
    
    # Get the database
    dbname = get_database()
    collection_name = dbname["members"]