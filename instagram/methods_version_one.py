import time
import re

from pydantic import ValidationError
from rest_framework import status

from instagram.base_functions import get_profile, manage_response, create_profile, update_profile, create_post, \
    publish_on_first_page, get_first_page, post_comment, like_post, start_to_follow, stop_to_follow, get_followers
from instagram.validators import ProfileValidator, PostValidator, CommentValidator, LikeValidator, \
    FollowingRelationValidator


# Profile Methods Version 1
def make_dict_profile(profile_obj):
    output_dict = {
        "id": str(profile_obj._id),
        "username": profile_obj.username,
        "first_name": profile_obj.first_name,
        "last_name": profile_obj.last_name,
        "picture": profile_obj.picture
    }
    return output_dict


def profile_data_constraints(data):
    try:
        ProfileValidator(**data)
    except ValidationError as e:
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

    profile_obj = create_profile(username, first_name, last_name, picture)
    output_dict = make_dict_profile(profile_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'profile': output_dict})
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
    output_dict = make_dict_profile(profile_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'profile': output_dict})
    return response


def get_profile_version_1(profile_id):
    profile_obj = get_profile(profile_id)
    output_dict = make_dict_profile(profile_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'profile': output_dict})
    return response


# Post Methods Version 2
def make_dict_post(post_obj):
    output_dict = {
        "id": str(post_obj._id),
        "image": post_obj.image,
        "caption": post_obj.caption,
        "tags": post_obj.tags,
        "publisher": str(post_obj.publisher),
        "published_date": post_obj.published_date
    }
    return output_dict


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
        'publisher': publisher_id,
        'published_date': time.time()
    }

    post_obj = create_post(new_data)
    # publish on first page of list_of_followings
    publish_on_first_page(publisher_id, str(post_obj._id))
    output_dict = make_dict_post(post_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'post': output_dict})
    return response


def get_first_page_version_1(owner_id):
    list_of_post_on_first_page = get_first_page(owner_id)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'posts': list_of_post_on_first_page})
    return response


def make_dict_comment(comment_obj):
    output_dict = {
        "post_id": str(comment_obj.post_id),
        "comment_post": comment_obj.comment_post,
        "author_id": str(comment_obj.author),
        "date": comment_obj.date
    }
    return output_dict


def post_comment_version_1(author_id, data):
    try:
        CommentValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    new_data = {
        'post_id': data.get("post_id"),
        'comment_post': data.get("comment_post"),
        'author': author_id,
        'date': time.time()
    }
    comment_obj = post_comment(new_data)
    output_dict = make_dict_comment(comment_obj)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'comment': output_dict})
    return response


def like_post_version_1(author_id, data):
    try:
        LikeValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    new_data = {
        'author': author_id,
        'post_id': data.get("post_id")
    }
    like_obj = like_post(new_data)
    output_dict = {
        'post_id': str(like_obj.post_id),
        'author': str(like_obj.author)
    }
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'like': output_dict})
    return response


def make_dict_follow(data):
    output_dict = {
        'username': data.username,
        'number_of_follower': data.number_of_follower,
        'number_of_following': data.number_of_following

    }
    print("output_dict : ", output_dict)
    return output_dict


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
        follow_obj = start_to_follow(following_id, follower_id)
    elif method == "stop":
        follow_obj = stop_to_follow(following_id, follower_id)

    follower_page = make_dict_follow(follow_obj[0])
    following_page = make_dict_follow(follow_obj[1])
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={'following_relation': {
                                   'following_page': following_page,
                                   'follower_page': follower_page
                               }})
    return response


def get_followers_version_1(following_id):
    list_of_followers_and_number = get_followers(following_id)
    response = manage_response(status=status.HTTP_200_OK,
                               status_info="ok",
                               data={
                                   'number_of_followers': list_of_followers_and_number[0],
                                   'followers_username': list_of_followers_and_number[1]
                               })
    return response

