import logging

from bson import ObjectId
from pymongo import MongoClient, ReturnDocument
from bson.json_util import dumps, loads
from LikeInstaProject.settings import MONGO_URI, MONGO_NAME
from instagram.models import Post, Profile

logger = logging.getLogger(__name__)


class MongoClientClass:
    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri, authSource="admin")
        self.mongo_db = self.mongo_client[MONGO_NAME]
        self.mongo_collection = ""

    def fetch_one_data(self, modelName, query: dict, **kwargs):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        found_dict = self.mongo_collection.find_one(query)
        if found_dict is None:
            raise Exception("Does Not Exist")
        if kwargs.get("count"):
            return found_dict.count()
        else:
            obj = modelName(**found_dict)
            return obj

    def fetch_data(self, modelName, query: dict, **kwargs):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        if kwargs.get("per_page_limit"):
            per_page = kwargs["per_page_limit"]
            founded_documents = self.mongo_collection.find(query).sort([('_id', -1), ]).limit(per_page)
        else:
            founded_documents = self.mongo_collection.find(query)
        data = dumps(list(founded_documents))
        return loads(data)

    def insert_one_data(self, modelName, kwargs):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        self.mongo_collection.insert_one(kwargs)
        obj = modelName(**kwargs)
        return obj

    def delete_one_data(self, modelName, kwargs):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        result = self.mongo_collection.delete_one(kwargs)
        if result.deleted_count == 0:
            raise Exception("Does Not Exist")

    def remove_data(self, modelName, kwargs):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        result = self.mongo_collection.remove(kwargs)
        return result

    def update_data(self, modelName, filter_query, update_query, upsert):
        db_collection = modelName._get_collection_name()
        self.mongo_collection = self.mongo_db[db_collection]
        updated_dict = self.mongo_collection.find_one_and_update(filter_query,
                                                                 update_query,
                                                                 return_document=ReturnDocument.AFTER,
                                                                 upsert=upsert)
        if updated_dict:
            obj = modelName(**updated_dict)
            return obj
        else:
            raise Exception("Does Not Exist")


mongo_client_obj = MongoClientClass(MONGO_URI)
