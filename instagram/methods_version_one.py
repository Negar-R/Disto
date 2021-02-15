import time
import logging
import re

from bson import ObjectId
from pydantic import ValidationError
from rest_framework import status

from instagram.base_functions import get_profile, manage_response, create_profile, update_profile, create_post, \
    publish_on_home_page, get_home_page, post_comment, like_post, start_to_follow, stop_to_follow, get_followers, \
    get_followings, unlike_post, get_page_post, get_comments, get_likes
from instagram.out_models import OutputGeneral
from instagram.serializers_input import ProfileValidator, PostValidator, CommentValidator, LikeValidator, \
    FollowingRelationValidator, PagePostsValidator
from instagram.serializers_output import ProfileSerializerVersionOne, PostSerializerVersion1, \
    EmbeddedPostSerializerVersionOne, EmbeddedUserSerializerVersionOne, EmbeddedCommentsSerializerVersionOne, \
    HomePageSerializerVersionOne, GetFollowingsSerializerVersionOne, ProfileFollowSerializerVersionOne, \
    GetFollowersSerializerVersionOne, PagePostSerializerVersionOne, CommentSerializerVersionOne, \
    LikeSerializerVersionOne, GeneralSerializerVersionOne


logger = logging.getLogger(__name__)


# Profile Methods Version 1
def profile_data_constraints(data):
    try:
        ProfileValidator(**data)
    except ValidationError as e:
        logger.error("profile_data_constraints/method : " + str(e))
        return "invalid"


def create_profile_version_1(data):
    try:
        validation = profile_data_constraints(data)
        if validation == "invalid":
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid",
                                       data={})
            return response

        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        picture = data.get("picture")

        output_profile_obj = create_profile(username, first_name, last_name, picture)
        serializer = ProfileSerializerVersionOne(output_profile_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'profile': serializer.data})
        return response
    except Exception as e:
        logger.error("create_profile_version_1/method : " + str(e))
        pass


def update_profile_version_1(profile_id, data):
    try:
        validation = profile_data_constraints(data)
        if validation == "invalid":
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid",
                                       data={})
            return response

        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        picture = data.get("picture")

        profile_obj = update_profile(profile_id, username, first_name, last_name, picture)
        serializer = ProfileSerializerVersionOne(profile_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'profile': serializer.data})
        return response
    except Exception as e:
        logger.error("update_profile_version_1/method : " + str(e))
        pass


def get_profile_version_1(profile_id):
    try:
        profile_obj = get_profile(profile_id)
        serializer = ProfileSerializerVersionOne(profile_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'profile': serializer.data})
        return response
    except Exception as e:
        logger.error("get_profile_version_1/method : " + str(e))
        pass


# Post Methods Version 1
def create_post_version_1(publisher_id, data):
    try:
        PostValidator(**data)
    except ValidationError as e:
        logger.error("PostValidator/method : ", str(e))
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response
    try:
        new_data = {
            'image': data.get("image"),
            'caption': data.get("caption"),
            'tags': re.findall("\B\#\w+", data.get("caption")),
            'publisher': ObjectId(publisher_id),
            'published_date': time.time()
        }

        output_create_post_obj = create_post(new_data)
        serializer = PostSerializerVersion1(output_create_post_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'post': serializer.data})
        return response
    except Exception as e:
        logger.error("create_post_version_1/method : " + str(e))
        pass


def get_home_page_version_1(owner_id, data):
    try:
        start_id = data.get("start_id")

        output_first_page_obj = get_home_page(owner_id, start_id)
        serializer = HomePageSerializerVersionOne(output_first_page_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'first_page': serializer.data})
        return response
    except Exception as e:
        logger.error("get_home_page_version_1/method : " + str(e))
        pass


def get_page_posts_version_1(data):
    try:
        PagePostsValidator(**data)
    except ValidationError as e:
        logger.error("PagePostsValidator/method : " + str(e))
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    try:
        profile_id = data.get("profile_id")

        output_page_post = get_page_post(profile_id)
        serializer = PagePostSerializerVersionOne(output_page_post)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'post_of_page': serializer.data})
        return response
    except Exception as e:
        logger.error("get_page_posts_version_1/method : " + str(e))
        pass


def post_comment_version_1(author_id, data):
    try:
        CommentValidator(**data)
    except ValidationError as e:
        logger.error("CommentValidator/method : " + str(e))
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    try:
        post_id = ObjectId(data.get("post_id"))
        comment_text = data.get("comment_text")
        tags = re.findall("\B\#\w+", comment_text),
        author_id = ObjectId(author_id)
        date = time.time()

        output_comment_obj = post_comment(post_id, comment_text, tags, author_id, date)
        serializer = EmbeddedCommentsSerializerVersionOne(output_comment_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'comment': serializer.data})
        return response
    except Exception as e:
        logger.error("post_comment_version_1/method : " + str(e))
        pass


def get_comments_version_1(data):
    try:
        post_id = data.get("post_id")

        output_comment_obj = get_comments(post_id)
        serializer = CommentSerializerVersionOne(output_comment_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'comments_of_post': serializer.data})
        return response
    except Exception as e:
        logger.error("get_comments_version_1/method : " + str(e))
        pass


def like_or_unlike_post_version_1(method, author_id, data):
    try:
        LikeValidator(**data)
    except ValidationError as e:
        logger.error("LikeValidator/method : " + str(e))
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response
    try:
        post_id = data.get("post_id")

        if method == "like":
            like_post(author_id, post_id)
        elif method == "unlike":
            unlike_post(author_id, post_id)

        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={})
        return response
    except Exception as e:
        logger.error("like_or_unlike_post_version_1/method : " + str(e))
        pass


def get_likes_version_1(data):
    try:
        post_id = data.get("post_id")

        output_like_obj = get_likes(post_id)
        serializer = LikeSerializerVersionOne(output_like_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'likes_of_post': serializer.data})
        return response
    except Exception as e:
        logger.error("get_likes_version_1/method : " + str(e))
        pass


def follow_version_1(method, following_id, data):
    try:
        FollowingRelationValidator(**data)
    except ValidationError as e:
        logger.error("FollowingRelationValidator/method : " + str(e))
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid",
                                   data={})
        return response

    try:
        follower_id = data.get("follower")

        if method == "start":
            start_to_follow(following_id, follower_id)
        elif method == "stop":
            stop_to_follow(following_id, follower_id)

        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={})
        return response
    except Exception as e:
        logger.error("follow_version_1/method : " + str(e))
        pass


def get_followers_version_1(data):
    try:
        following_id = data.get("following_id")

        output_followers_obj = get_followers(following_id)
        serializer = GetFollowersSerializerVersionOne(output_followers_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'followers': serializer.data})
        return response
    except Exception as e:
        logger.error("get_followers_version_1/method : " + str(e))
        pass


def get_followings_version_1(data):
    try:
        follower_id = data.get("follower_id")

        output_followings_obj = get_followings(follower_id)
        serializer = GetFollowingsSerializerVersionOne(output_followings_obj)
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="ok",
                                   data={'followings': serializer.data})
        return response
    except Exception as e:
        logger.error("get_followings_version_1/method : " + str(e))
        pass

