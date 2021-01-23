from pymongo import MongoClient
from LikeInstaProject.settings import MONGO_URI, MONGO_NAME
from pymongo.collection import Collection


class MongoClientClass:
    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri, authSource="admin")
        self.mongo_db = self.mongo_client[MONGO_NAME]
        self.mongo_collection = ""

    def fetch_data(self, dbcollection: str):
        self.mongo_collection = self.mongo_db[dbcollection]
        data = self.mongo_collection.find()
        return data

    def insert_data(self, dbcollection: str, **kwargs):
        print("HERE IN INSERT @@@ ", " DB : ", dbcollection, " LIST : ", kwargs)
        self.mongo_collection = self.mongo_db[dbcollection]

        data = self.mongo_collection.insert_one(kwargs)
        print("INSERTED @@")
        return data


mongo_client_obj = MongoClientClass(MONGO_URI)
