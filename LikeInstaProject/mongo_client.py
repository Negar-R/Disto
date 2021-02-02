from bson import ObjectId
from pymongo import MongoClient
from bson.json_util import dumps, loads
from LikeInstaProject.settings import MONGO_URI, MONGO_NAME
from instagram.models import Post, Profile


class MongoClientClass:
    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri, authSource="admin")
        self.mongo_db = self.mongo_client[MONGO_NAME]
        self.mongo_collection = ""

    def fetch_one_data(self, modelName, query: str, query_param):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        found_dict = self.mongo_collection.find_one({query: query_param})
        obj = modelName(**found_dict)
        return obj

    def fetch_data(self, modelName, query: str, query_param):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        data = dumps(list(self.mongo_collection.find({query: query_param})))
        return loads(data)

    def insert_one_data(self, modelName, kwargs):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        self.mongo_collection.insert_one(kwargs)
        obj = modelName(**kwargs)
        return obj

    def delete_one_data(self, dbcollection: str, kwargs):
        self.mongo_collection = self.mongo_db[dbcollection]
        self.mongo_collection.delete_one(kwargs)

    def update_data(self, modelName, filter_query, update_query, upsert):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        updated_dict = self.mongo_collection.find_one_and_update(filter_query,
                                                                 update_query,
                                                                 upsert=upsert)
        obj = modelName(**updated_dict)
        return obj


mongo_client_obj = MongoClientClass(MONGO_URI)
