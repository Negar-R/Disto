from bson import ObjectId
from pydantic import ValidationError
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.json_util import dumps, loads
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from LikeInstaProject.mongo_client import mongo_client_obj
from instagram.models import Profile, Post
from instagram.validators import ProfileValidator, ProfileBodyRequestValidator, \
    FollowingRelationValidator, FollowingRelationBodyValidator, PostValidator, ReactionKindValidator
import re
import time
import json

# Create your views here.

# POST VIEWS
class FollowAPIView(APIView):
    """
    GET : see list of followers
    POST : started to follow some body that its id be in the body of request
    DELETE: delete one of your following
    """

    def post(self, request, format=None):
        data_constraints(FollowingRelationBodyValidator, request.data)
        data_constraints(FollowingRelationValidator, request.data.get("data"))

        following_id = ObjectId(request.data["data"]["following"])
        follower_id = ObjectId(request.data["data"]["follower"])

        if request.data.get("method") == "start_to_follow":
            mongo_client_obj.insert_one_data('following_relation', **{'following': following_id,
                                                                      'follower': follower_id})
            mongo_client_obj.update_data('profiles',
                                         {'_id': following_id},
                                         {"$inc": {'number_of_follower': 1}},
                                         upsert=False)
            mongo_client_obj.update_data('profiles',
                                         {'_id': follower_id},
                                         {"$inc": {'number_of_following': 1}},
                                         upsert=False)
            return Response("You are started to follow", status=status.HTTP_200_OK)

        elif request.data.get("method") == "stop_to_follow":
            mongo_client_obj.delete_one_data('following_relation', **{'following': following_id,
                                                                      'follower': follower_id})
            # decrease the number of followers and followings
            mongo_client_obj.update_data('profiles',
                                         {'_id': following_id},
                                         {"$inc": {'number_of_follower': -1}},
                                         upsert=False)
            mongo_client_obj.update_data('profiles',
                                         {'_id': follower_id},
                                         {"$inc": {'number_of_following': -1}},
                                         upsert=False)
            return Response("You are stopped to follow", status=status.HTTP_200_OK)

        elif request.data.get("method") == "get_followers":
            list_of_follow = mongo_client_obj.fetch_data('following_relation',
                                                         'following', following_id)
            list_of_followers_id = []
            for f in list_of_follow:
                list_of_followers_id.append(f["follower"])

            # TODO : return objects of data in fetch_data
            list_of_followers_profile = mongo_client_obj.fetch_data('profiles',
                                                                    '_id',
                                                                    {"$in": list_of_followers_id}
                                                                    )

            returned_profile_list = []
            for p in list_of_followers_profile:
                obj = Profile(**p)
                json_of_obj = {
                    'username': obj.username,
                    'first_name': obj.first_name,
                    'last_name': obj.last_name
                }
                returned_profile_list.append(json_of_obj)

            return Response(returned_profile_list, status=status.HTTP_200_OK)
