import time
import logging
import re

from bson import ObjectId
from pydantic import ValidationError

from instagram.base_functions import get_profile, manage_response, create_profile, update_profile, create_post, \
    publish_on_home_page, get_home_page, post_comment, like_post, start_to_follow, stop_to_follow, get_followers, \
    get_followings, unlike_post, get_page_post, get_comments, get_likes, search_tags, search_account, \
    determine_follow_request, get_applicant_users, delete_following, block_or_unblock_following, get_blocked_following
from instagram.out_models import OutputGeneral
from instagram.serializers_input import ProfileValidator, PostValidator, CommentValidator, LikeValidator, \
    FollowingRelationValidator, PagePostsValidator, SearchValidator, DetermineFollowRequest, DeleteFollowingValidator
from instagram.serializers_output import ProfileSerializerVersionOne, PostSerializerVersion1, \
    EmbeddedPostSerializerVersionOne, EmbeddedUserSerializerVersionOne, EmbeddedCommentsSerializerVersionOne, \
    HomePageSerializerVersionOne, GetFollowingsSerializerVersionOne, ProfileFollowSerializerVersionOne, \
    GetFollowersSerializerVersionOne, PagePostSerializerVersionOne, CommentSerializerVersionOne, \
    LikeSerializerVersionOne, GeneralSerializerVersionOne


logger = logging.getLogger(__name__)


def search_data_constraints(data):
    try:
        SearchValidator(**data)
    except ValidationError as e:
        logger.error("SearchValidator/serializers_input : " + str(e))
        return "invalid"


# Profile Methods Version 1
def profile_data_constraints(data):
    try:
        ProfileValidator(**data)
    except ValidationError as e:
        logger.error("profile_data_constraints/serializers_input : " + str(e))
        return "invalid"


def create_profile_version_1(data):
    try:
        validation = profile_data_constraints(data)
        if validation == "invalid":
            response = manage_response(status_info="invalid",
                                       data={})
            return response

        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        # picture = data.get("picture")
        private = data.get("private")

        output_profile_obj = create_profile(username, first_name, last_name, private)
        serializer = ProfileSerializerVersionOne(output_profile_obj)
        response = manage_response(status_info="ok",
                                   data={'profile': serializer.data})
        return response
    except Exception as e:
        logger.error("create_profile_version_1/method : " + str(e))
        raise Exception(str(e))


def update_profile_version_1(profile_id, data):
    try:
        validation = profile_data_constraints(data)
        if validation == "invalid":
            response = manage_response(status_info="invalid",
                                       data={})
            return response

        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        # picture = data.get("picture")
        private = data.get("private")

        profile_obj = update_profile(profile_id, username, first_name, last_name, private)
        serializer = ProfileSerializerVersionOne(profile_obj)
        response = manage_response(status_info="ok",
                                   data={'profile': serializer.data})
        return response
    except Exception as e:
        logger.error("update_profile_version_1/method : " + str(e))
        raise Exception(str(e))


def get_profile_version_1(profile_id):
    try:
        profile_obj = get_profile(profile_id)
        serializer = ProfileSerializerVersionOne(profile_obj)
        response = manage_response(status_info="ok",
                                   data={'profile': serializer.data})
        return response
    except Exception as e:
        logger.error("get_profile_version_1/method : " + str(e))
        raise Exception(str(e))


# Post Methods Version 1
def create_post_version_1(publisher_id, data):
    try:
        PostValidator(**data)
    except ValidationError as e:
        logger.error("PostValidator/serializers_input : ", str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response
    try:
        caption = data.get("caption")
        uniqueness_tags = [tag.strip("#") for tag in caption.split() if tag.startswith("#")]
        tags = list(set(uniqueness_tags))
        new_data = {
            'image': data.get("image"),
            'caption': caption,
            'tags': tags,
            'publisher': ObjectId(publisher_id),
            'published_date': time.time()
        }

        output_create_post_obj = create_post(new_data)
        serializer = PostSerializerVersion1(output_create_post_obj)
        response = manage_response(status_info="ok",
                                   data={'post': serializer.data})
        return response
    except Exception as e:
        logger.error("create_post_version_1/method : " + str(e))
        raise Exception(str(e))


def get_home_page_version_1(owner_id, data):
    try:
        start_id = data.get("start_id")

        output_first_page_obj = get_home_page(owner_id, start_id)
        serializer = HomePageSerializerVersionOne(output_first_page_obj)
        response = manage_response(status_info="ok",
                                   data={'first_page': serializer.data})
        return response
    except Exception as e:
        logger.error("get_home_page_version_1/method : " + str(e))
        raise Exception(str(e))


def get_page_posts_version_1(data):
    try:
        PagePostsValidator(**data)
    except ValidationError as e:
        logger.error("PagePostsValidator/serializers_input : " + str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response

    try:
        profile_id = data.get("profile_id")
        start_id = data.get("start_id")

        output_page_post = get_page_post(profile_id, start_id)
        serializer = PagePostSerializerVersionOne(output_page_post)
        response = manage_response(status_info="ok",
                                   data={'post_of_page': serializer.data})
        return response
    except Exception as e:
        logger.error("get_page_posts_version_1/method : " + str(e))
        raise Exception(str(e))


def post_comment_version_1(author_id, data):
    try:
        CommentValidator(**data)
    except ValidationError as e:
        logger.error("CommentValidator/serializers_input : " + str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response

    try:
        post_id = ObjectId(data.get("post_id"))
        comment_text = data.get("comment_text")
        uniqueness_tags = [tag.strip("#") for tag in comment_text.split() if tag.startswith("#")]
        tags = list(set(uniqueness_tags))
        author_id = ObjectId(author_id)
        date = time.time()

        output_comment_obj = post_comment(post_id, comment_text, tags, author_id, date)
        serializer = EmbeddedCommentsSerializerVersionOne(output_comment_obj)
        response = manage_response(status_info="ok",
                                   data={'comment': serializer.data})
        return response
    except Exception as e:
        logger.error("post_comment_version_1/method : " + str(e))
        raise Exception(str(e))


def get_comments_version_1(data):
    try:
        post_id = data.get("post_id")
        start_id = data.get("start_id")

        output_comment_obj = get_comments(post_id, start_id)
        serializer = CommentSerializerVersionOne(output_comment_obj)
        response = manage_response(status_info="ok",
                                   data={'comments_of_post': serializer.data})
        return response
    except Exception as e:
        logger.error("get_comments_version_1/method : " + str(e))
        raise Exception(str(e))


def like_or_unlike_post_version_1(method, author_id, data):
    try:
        LikeValidator(**data)
    except ValidationError as e:
        logger.error("LikeValidator/serializers_input : " + str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response
    try:
        post_id = data.get("post_id")

        if method == "like":
            message = like_post(author_id, post_id)
        elif method == "unlike":
            message = unlike_post(author_id, post_id)

        response = manage_response(status_info="ok",
                                   data={'message': message})
        return response
    except Exception as e:
        logger.error("like_or_unlike_post_version_1/method : " + str(e))
        raise Exception(str(e))


def get_likes_version_1(data):
    try:
        post_id = data.get("post_id")
        start_id = data.get("start_id")

        output_like_obj = get_likes(post_id, start_id)
        serializer = LikeSerializerVersionOne(output_like_obj)
        response = manage_response(status_info="ok",
                                   data={'likes_of_post': serializer.data})
        return response
    except Exception as e:
        logger.error("get_likes_version_1/method : " + str(e))
        raise Exception(str(e))


def follow_version_1(method, following_id, data):
    try:
        FollowingRelationValidator(**data)
    except ValidationError as e:
        logger.error("FollowingRelationValidator/serializers_input : " + str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response

    try:
        follower_id = data.get("follower")

        if method == "start":
            returned_message = start_to_follow(following_id, follower_id)
        elif method == "stop":
            returned_message = stop_to_follow(following_id, follower_id)
        response = manage_response(status_info="ok",
                                   data={'message': returned_message})
        return response
    except Exception as e:
        logger.error("follow_version_1/method : " + str(e))
        raise Exception(str(e))


def delete_following_version_1(auth, data):
    try:
        DeleteFollowingValidator(**data)
    except ValidationError as e:
        logger.error("DeleteFollowingValidator/serializers_input : " + str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response

    try:
        following_id = data.get("following")

        returned_message = delete_following(auth, following_id)
        response = manage_response(status_info="ok",
                                   data={'message': returned_message})
        return response
    except Exception as e:
        logger.error("delete_following_version_1/method : " + str(e))
        raise Exception(str(e))


def determine_follow_request_version_1(auth, data):
    try:
        DetermineFollowRequest(**data)
    except ValidationError as e:
        logger.error("DetermineFollowRequest/serializers_input : " + str(e))
        response = manage_response(status_info="invalid",
                                   data={})
        return response

    action = data.get('action')
    follower_id = data.get("follower_id")

    returned_message = determine_follow_request(action, auth, follower_id)
    response = manage_response(status_info="ok",
                               data={"message": returned_message})
    return response


# TODO: test this function and make the get_followers function correct
def get_followers_version_1(auth, data):
    try:
        user_id = data.get("user_id")
        start_id = data.get("start_id")

        output_followers_obj = get_followers(auth, user_id, start_id)
        serializer = GetFollowersSerializerVersionOne(output_followers_obj)
        response = manage_response(status_info="ok",
                                   data={'followers': serializer.data})
        return response
    except Exception as e:
        logger.error("get_followers_version_1/method : " + str(e))
        raise Exception(str(e))


def get_followings_version_1(auth, data):
    try:
        user_id = data.get("user_id")
        start_id = data.get("start_id")

        output_followings_obj = get_followings(auth, user_id, start_id)
        serializer = GetFollowingsSerializerVersionOne(output_followings_obj)
        response = manage_response(status_info="ok",
                                   data={'followings': serializer.data})
        return response
    except Exception as e:
        logger.error("get_followings_version_1/method : " + str(e))
        raise Exception(str(e))


def get_applicant_users_version_1(auth, data):
    try:
        start_id = data.get("start_id")

        output_applicant_users = get_applicant_users(auth, start_id)
        serializer = GetFollowersSerializerVersionOne(output_applicant_users)
        response = manage_response(status_info="ok",
                                   data={'requested_users': serializer.data})
        return response

    except Exception as e:
        logger.error("get_applicant_users_version_1/method : " + str(e))
        raise Exception(str(e))


def blocking_or_unblocking_following_version_1(auth, data):
    try:
        action = data.get("action")
        following_id = data.get("following_id")

        returned_message = block_or_unblock_following(action, auth, following_id)
        response = manage_response(status_info="ok",
                                   data={'message': returned_message})
        return response

    except Exception as e:
        logger.error("blocking_or_unblocking_follower_version_1/method : " + str(e))
        raise Exception(str(e))


def get_blocked_following_version_1(auth, data):
    try:
        start_id = data.get("start_id")

        output_blocked_followings_obj = get_blocked_following(auth, start_id)
        serializer = GetFollowingsSerializerVersionOne(output_blocked_followings_obj)
        response = manage_response(status_info="ok",
                                   data={'followings': serializer.data})
        return response

    except Exception as e:
        logger.error("get_blocked_following_version_1/method : " + str(e))
        raise Exception(str(e))


def search_tags_version_1(data):
    try:
        validation = search_data_constraints(data)
        if validation == "invalid":
            response = manage_response(status_info="invalid",
                                       data={})
            return response

        search_value = data.get("search_value")
        start_id = data.get("start_id")

        output_search_obj = search_tags(search_value, start_id)
        serializer = PagePostSerializerVersionOne(output_search_obj)
        response = manage_response(status_info="ok",
                                   data={'founded_post': serializer.data})
        return response
    except Exception as e:
        logger.error("search_tags_version_1/method : " + str(e))
        raise Exception(str(e))


def search_account_version_1(data):
    try:
        validation = search_data_constraints(data)
        if validation == "invalid":
            response = manage_response(status_info="invalid",
                                       data={})
            return response

        username = data.get("search_value")
        start_id = data.get("start_id")

        output_search_obj = search_account(username, start_id)
        serializer = GetFollowersSerializerVersionOne(output_search_obj)
        response = manage_response(status_info="ok",
                                   data={'profiles': serializer.data})
        return response
    except Exception as e:
        logger.error("search_account_version_1/method : " + str(e))
        raise Exception(str(e))
