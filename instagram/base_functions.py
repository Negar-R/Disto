import time

from bson import ObjectId

from LikeInstaProject import mongo_client_obj
from instagram.models import Profile


def manage_response(status, status_info, data):
    response = {
        'status': status,
        'status_info': status_info,
        'data': data
    }
    return response


def create_profile(username, first_name, last_name, picture):
    data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'picture': picture,
        'date_of_join': time.time()
    }
    profile_obj = mongo_client_obj.insert_one_data(Profile, data)
    return profile_obj


def update_profile(profile_id, username, first_name, last_name, picture):
    data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'picture': picture,
    }
    profile_obj = mongo_client_obj.update_data(Profile,
                                               {'_id': ObjectId(profile_id)},
                                               {"$set": data},
                                               upsert=False)
    return profile_obj


def get_profile(profile_id):
    profile_obj = mongo_client_obj.fetch_one_data(Profile, '_id', ObjectId(profile_id))
    return profile_obj
