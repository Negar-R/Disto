from bson import ObjectId
from django.http import Http404
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.json_util import dumps, loads
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from LikeInstaProject.mongoClient import mongo_client_obj
from instagram.serializers import ProfileSerializer, FollowingRelationSerializer, PostSerializer
import time
import json

# Create your views here.


# PROFILE VIEWS
class ProfileAPIView(APIView):
    """
    Create a profile
    """

    def post(self, request, format=None):
        serializer = ProfileSerializer(data=request.data.get("data"))
        if serializer.is_valid():
            if request.data.get("method") == "create_profile":
                request.data["date"] = time.time()
                mongo_client_obj.insert_one_data('profiles', **request.data)
                return Response("Your profile created successfully", status=status.HTTP_201_CREATED)

            elif request.data.get("method") == "update_profile":
                profile_id = ObjectId(request.data.get("obj_id"))
                mongo_client_obj.update_one_profile('profiles', '_id', profile_id, **serializer.data)
                return Response("Your Profile updated successfully", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProfileAPIViewDetail(APIView):
    """
    GET, PUT, DELETE a profile by passing a username in URL
    """

    def get(self, request, username, format=None):
        try:
            profile_obj = mongo_client_obj.fetch_one_data('profiles', 'username', username)
        except:
            raise Http404
        serializer = ProfileSerializer(profile_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


# POST VIEWS
class FollowAPIView(APIView):
    """
    GET : see list of followers
    POST : started to follow some body that its id be in the body of request
    DELETE: delete one of your following
    """

    def get(self, request, id, format=None):
        try:
            list_of_followers = list(mongo_client_obj.fetch_data('following_relation',
                                                                 'following', ObjectId(id)))
        except:
            raise Http404
        json_of_followers = dumps(list_of_followers)
        serializer = FollowingRelationSerializer(loads(json_of_followers))
        # return id of all followers in list
        ans = []
        for obj in serializer.instance:
            ans.append(str(obj['follower']))
        return Response(ans, status=status.HTTP_200_OK)

    def post(self, request, id, format=None):
        serializer = FollowingRelationSerializer(data=request.data)
        if serializer.is_valid():
            following_id = ObjectId(id)
            follower_id = ObjectId(serializer.data.get('follower'))
            mongo_client_obj.insert_one_data('following_relation', **{'following': following_id,
                                                                      'follower': follower_id})
            # increase the number of followers and followings
            collection = mongo_client_obj.mongo_db['profiles']
            collection.update_one({'_id': following_id}, {"$inc": {'number_of_follower': 1}},
                                 upsert=False)
            collection.update_one({'_id': follower_id}, {"$inc": {'number_of_following': 1}},
                                 upsert=False)
            return Response("You are started to follow", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        serializer = FollowingRelationSerializer(data=request.data)
        if serializer.is_valid():
            following_id = ObjectId(id)
            follower_id = ObjectId(serializer.data.get('follower'))
            mongo_client_obj.delete_one_data('following_relation', **{'following': following_id,
                                                                      'follower': follower_id})
            # decrease the number of followers and followings
            collection = mongo_client_obj.mongo_db['profiles']
            collection.update_one({'_id': following_id}, {"$inc": {'number_of_follower': -1}},
                                  upsert=False)
            collection.update_one({'_id': follower_id}, {"$inc": {'number_of_following': -1}},
                                  upsert=False)
            return Response("You are stopped to follow", status=status.HTTP_200_OK)


class PostAPIView(APIView):
    """
    POST : publish one post and also add it tho the first page of publisher's followings
    """

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # convert publisher_id string to ObjectId
            publisher = ObjectId(serializer.data.get('publisher'))
            # create post objects
            request.data["published_date"] = time.time()
            request.data["publisher"] = publisher
            post = mongo_client_obj.insert_one_data('posts', **request.data)

            # update the first page of the publisher's following
            list_of_followings = mongo_client_obj.fetch_data('following_relation', 'follower', publisher)
            for follow_relation in list_of_followings:
                following = follow_relation["following"]
                mongo_client_obj.update_first_page('first_page', 'owner', following, post.inserted_id)
            return Response("Your post has been published")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FirstPageAPIView(APIView):
    """
    GET : show post of followers in the first page
    """

    def get(self, request, owner_id):
        owner_id = ObjectId(owner_id)
        first_page = mongo_client_obj.fetch_data('first_page', 'owner', owner_id)
        first_page = loads(dumps(first_page))[0]
        posts = first_page["inclusive_pots"]
        list_of_post_in_page = []
        for po in posts:
            post = mongo_client_obj.fetch_one_data('posts', '_id', po)

            show_post = {}
            show_post["publisher"] = str(post.get("publisher"))
            show_post["image"] = post.get("image")
            show_post["caption"] = post.get("caption")
            show_post["tags"] = post.get("tags")
            show_post["comments"] = post.get("comments")
            show_post["likes"] = post.get("likes")

            list_of_post_in_page.append(show_post)
        return Response(list_of_post_in_page, status=status.HTTP_200_OK)


@csrf_exempt
def reactOnPostAPIView(request, post_id):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        msg = json.loads(body)
        reaction_kind = msg.get('reaction_kind')
        post_id = ObjectId(post_id)
        collection = mongo_client_obj.mongo_db['posts']

        if reaction_kind == "like":
            print("IN LIKE $$$ ")
            collection.update_one({'_id': post_id},
                                  {"$inc": {'likes': 1}},
                                  upsert=False)
            return JsonResponse({"message": "You like this post"})

        elif reaction_kind == "comment":
            # create a comment object
            comment_content = {}
            comment_content["comment_post"] = msg["data"]["comment_post"]
            comment_content["author"] = ObjectId(msg["data"]["author_id"])
            comment_content["date"] = time.time()
            posted_comment = mongo_client_obj.insert_one_data('comments', **comment_content)

            # add posted comment to list of post's comments
            collection.update_one({'_id': post_id},
                                  {"$push": {"comments": posted_comment.inserted_id}},
                                  upsert=False)

            return JsonResponse({"message": "You commented on this post"})

