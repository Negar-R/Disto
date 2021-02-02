from bson import ObjectId
from pydantic import ValidationError
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.json_util import dumps, loads
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from LikeInstaProject.mongoClient import mongo_client_obj
from instagram.models import Profile, Post
from instagram.validators import ProfileValidator, ProfileBodyRequestValidator, \
    FollowingRelationValidator, FollowingRelationBodyValidator, PostValidator, ReactionKindValidator
import re
import time
import json

# Create your views here.


def data_constraints(name_of_validator, data):
    try:
        return name_of_validator(**data)
    except ValidationError as e:
        raise ValueError(e.errors())


# PROFILE VIEWS
class ProfileAPIView(APIView):
    """
    Create, Update, Get a profile
    """

    def post(self, request, format=None):
        data_constraints(ProfileBodyRequestValidator, request.data)

        if request.data.get("method") == "create_profile":
            data_constraints(ProfileValidator, request.data.get("new_data"))
            request.data["new_data"]["date_of_join"] = time.time()
            mongo_client_obj.insert_one_data('profiles', **request.data.get("new_data"))
            obj = Profile(**request.data.get("new_data"))
            return Response({"username": obj.username,
                             "first_name": obj.first_name,
                             "last_name": obj.last_name,
                             "picture": str(obj.picture)}, status=status.HTTP_201_CREATED)

        elif request.data.get("method") == "update_profile":
            data_constraints(ProfileValidator, request.data.get("new_data"))
            profile_id = ObjectId(request.data["get_info"]["obj_id"])
            obj = mongo_client_obj.update_one_profile('profiles', '_id', profile_id,
                                                      **request.data.get("new_data"))
            return Response([obj.username,
                             obj.first_name,
                             obj.last_name,
                             str(obj.picture)], status=status.HTTP_200_OK)

        elif request.data.get("method") == "get_profile":
            try:
                username = request.data["get_info"]["username"]
                profile = mongo_client_obj.fetch_one_data('profiles', 'username', username)
                return Response({"username": profile.username,
                                 "first_name": profile.first_name,
                                 "last_name": profile.last_name}, status=status.HTTP_200_OK)
            except Exception as e:
                raise Http404


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


class PostAPIView(APIView):
    """
    POST : publish one post and also add it tho the first page of publisher's followings
    """

    def post(self, request, format=None):
        try:
            PostValidator(**request.data)
            # convert publisher_id string to ObjectId
            publisher = ObjectId(request.data.get('publisher'))
            # create post objects
            request.data["published_date"] = time.time()
            request.data["publisher"] = publisher
            txt = request.data["caption"]
            tags = re.findall("\B\#\w+", txt)
            request.data["tags"] = tags
            mongo_client_obj.insert_one_data('posts', **request.data)
            post = Post(**request.data)
            # update the first page of the publisher's following
            list_of_followings = mongo_client_obj.fetch_data('following_relation', 'follower', publisher)
            for follow_relation in list_of_followings:
                following = follow_relation["following"]

                mongo_client_obj.update_first_page('first_page', 'owner', following, post.id)

            return Response({"caption": post.caption,
                             "tags": post.tags,
                             "image": str(post.image),
                             "publisher": str(post.publisher)}, status=status.HTTP_200_OK)

        except ValidationError as e:
            print(e.errors())
            return Response("invalid input !", status=status.HTTP_200_OK)


class FirstPageAPIView(APIView):
    """
    GET : show post of followers in the first page
    """

    def get(self, request, owner_id):
        owner_id = ObjectId(owner_id)
        first_page = mongo_client_obj.fetch_data('first_page', 'owner', owner_id)
        try:
            posts = first_page[0]["inclusive_pots"]
            list_of_post_in_page = []
            for post_id in posts:
                post = mongo_client_obj.fetch_one_data('posts', '_id', post_id)
                try:
                    list_of_post_in_page.append(
                        {
                            'publisher': str(post.publisher),
                            'image': str(post.image),
                            'caption': post.caption,
                            'tags': post.tags,
                            'likes': post.likes
                        }
                    )
                except Exception as e:
                    pass
            return Response(list_of_post_in_page, status=status.HTTP_200_OK)
        except IndexError:
            return Response("Empty page", status=status.HTTP_200_OK)


@csrf_exempt
def reactOnPostAPIView(request, post_id):
    """
    :param request:
    :param post_id: id of post that want react(like or comment) on it.
    :return: message
    """

    if request.method == 'POST':
        body = request.body.decode('utf-8')
        msg = json.loads(body)
        try:
            ReactionKindValidator(**msg)
            reaction_kind = msg.get('reaction_kind')
            post_id = ObjectId(post_id)

            if reaction_kind == "like":
                mongo_client_obj.update_data('posts',
                                             {'_id': post_id},
                                             {"$inc": {'likes': 1}},
                                             upsert=False)
                author_id = msg["data"]["author_id"]
                mongo_client_obj.insert_one_data('likes', **{'post_id': post_id, 'author': author_id})
                return JsonResponse({"message": "You like this post"})

            elif reaction_kind == "comment":
                # create a comment object
                comment_content = {}
                comment_content["comment_post"] = msg["data"]["comment_post"]
                comment_content["post_id"] = ObjectId(post_id)
                comment_content["author"] = ObjectId(msg["data"]["author_id"])
                comment_content["date"] = time.time()
                mongo_client_obj.insert_one_data('comments', **comment_content)

                return HttpResponse("You commented on this post", status=status.HTTP_200_OK)

        except ValidationError as e:
            return HttpResponse("invalid input !", status=status.HTTP_200_OK)
