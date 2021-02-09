import time
import re

from bson import ObjectId
from pydantic import ValidationError
from rest_framework import status

from instagram.base_functions import get_profile, manage_response, create_profile, update_profile, create_post, \
    publish_on_first_page, get_first_page, post_comment, like_post, start_to_follow, stop_to_follow, get_followers, \
    get_followings, unlike_post, get_page_post, get_comment
from instagram.validators import ProfileValidator, PostValidator, CommentValidator, LikeValidator, \
    FollowingRelationValidator, PagePostsValidator
from instagram.serializers import ProfileSerializerVersionOne, CreatePostSerializerVersion1, \
    EmbeddedPostSerializerVersionOne, EmbeddedUserSerializerVersionOne, EmbeddedCommentsSerializerVersionOne, \
    FirstPageSerializerVersionOne, GetFollowingsSerializerVersionOne, ProfileFollowSerializerVersionOne, \
    GetFollowersSerializerVersionOne, PagePostSerializerVersionOne, CommentSerializerVersionOne


# Profile Methods Version 1
def profile_data_constraints(data):
    try:
        ProfileValidator(**data)
    except ValidationError as e:
        print("## ", e.errors())
        return "invalid"


def create_profile_version_1(data):
    validation = profile_data_constraints(data)
    if validation == "invalid":
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    username = data["username"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    picture = data["picture"]

    output_profile_obj = create_profile(username, first_name, last_name, picture)
    serializer = ProfileSerializerVersionOne(output_profile_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'profile': serializer.data})
    return response


def update_profile_version_1(profile_id, data):
    validation = profile_data_constraints(data)
    if validation == "invalid":
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    username = data["username"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    picture = data["picture"]

    profile_obj = update_profile(profile_id, username, first_name, last_name, picture)
    serializer = ProfileSerializerVersionOne(profile_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'profile': serializer.data})
    return response


def get_profile_version_1(profile_id):
    profile_obj = get_profile(profile_id)
    serializer = ProfileSerializerVersionOne(profile_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'profile': serializer.data})
    return response


# Post Methods Version 1
def create_post_version_1(publisher_id, data):
    try:
        PostValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    new_data = {
        'image': data.get("image"),
        'caption': data.get("caption"),
        'tags': re.findall("\B\#\w+", data.get("caption")),
        'publisher': ObjectId(publisher_id),
        'published_date': time.time()
    }

    output_create_post_obj = create_post(new_data)
    serializer = CreatePostSerializerVersion1(output_create_post_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'post': serializer.data})
    return response


def get_first_page_version_1(owner_id):
    output_first_page_obj = get_first_page(owner_id)
    serializer = FirstPageSerializerVersionOne(output_first_page_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'first_page': serializer.data})
    return response


def get_page_posts_version_1(data):
    try:
        PagePostsValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    output_page_post = get_page_post(data.get("profile_id"))
    serializer = PagePostSerializerVersionOne(output_page_post)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'post_of_page': serializer.data})
    return response


def post_comment_version_1(author_id, data):
    try:
        CommentValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    post_id = ObjectId(data.get("post_id"))
    comment_post = data.get("comment_post")
    author_id = ObjectId(author_id)
    date = time.time()

    output_comment_obj = post_comment(post_id, comment_post, author_id, date)
    serializer = EmbeddedCommentsSerializerVersionOne(output_comment_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'comment': serializer.data})
    return response


def get_comment_version_1(data):
    post_id = data.get("post_id")
    output_comment_obj = get_comment(post_id)
    serializer = CommentSerializerVersionOne(output_comment_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'comments_of_post': serializer.data})
    return response


def like_or_unlike_post_version_1(method, author_id, data):
    try:
        LikeValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    new_data = {
        'author': ObjectId(author_id),
        'post_id': data.get("post_id")
    }
    if method == "like":
        like_post(new_data)
    elif method == "unlike":
        unlike_post(new_data)

    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={})
    return response


def follow_version_1(method, following_id, data):
    try:
        FollowingRelationValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    follower_id = data.get("follower")

    if method == "start":
        start_to_follow(following_id, follower_id)
    elif method == "stop":
        stop_to_follow(following_id, follower_id)

    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={})
    return response


def get_followers_version_1(data):
    following_id = data.get("following_id")
    output_followers_obj = get_followers(following_id)
    serializer = GetFollowersSerializerVersionOne(output_followers_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'followers': serializer.data})
    return response


def get_followings_version_1(data):
    follower_id = data.get("follower_id")
    output_followings_obj = get_followings(follower_id)
    serializer = GetFollowingsSerializerVersionOne(output_followings_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'followings': serializer.data})
    return response

