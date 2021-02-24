import time
import logging

from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from instagram.base_functions import manage_response
from instagram.methods_version_one import get_profile_version_1, create_profile_version_1, update_profile_version_1, \
    create_post_version_1, get_home_page_version_1, post_comment_version_1, follow_version_1, \
    get_followers_version_1, get_followings_version_1, like_or_unlike_post_version_1, get_page_posts_version_1, \
    get_comments_version_1, get_likes_version_1, search_tags_version_1, search_account_version_1, \
    determine_follow_request_version_1, get_applicant_users_version_1, delete_following_version_1, \
    blocking_or_unblocking_following_version_1, get_blocked_following_version_1, delete_picture_version_1
from instagram.out_models import OutputGeneral
from instagram.serializers_input import BodyStructureValidator
from instagram.serializers_output import GeneralSerializerVersionOne

logger = logging.getLogger(__name__)
list_of_exists_api_version = [1, ]


def check_body_of_request(data):
    try:
        BodyStructureValidator(**data)
    except ValidationError as e:
        response = manage_response(status_info="invalid input",
                                   data={})
        return False


# Profile View
class InstagramAPIView(APIView):

    def post(self, request):

        try:
            start_time = time.time()

            valid = check_body_of_request(request.data)
            ver_api = request.data.get("ver_api")
            if valid is False or ver_api not in list_of_exists_api_version:
                response = manage_response(status_info="invalid input",
                                           data={})
                return Response(response)

            if ver_api == 1:
                method = request.data.get("method")
                data = request.data.get("data")
                auth = request.data.get("auth")
                platform = request.data.get("platform")
                lang_code = request.data.get("lang_code")
                flag = True

                if method == "createProfile":
                    response = create_profile_version_1(data)

                elif method == "updateProfile":
                    # auth = profile_id
                    response = update_profile_version_1(auth, data)

                elif method == "getProfile":
                    profile_id = request.data["data"]["profile_id"]
                    response = get_profile_version_1(profile_id)

                elif method == "createPost":
                    # auth = publisher_id
                    response = create_post_version_1(auth, data)

                elif method == "getPagePosts":
                    response = get_page_posts_version_1(data)

                elif method == "getHomePage":
                    # auth = owner_id
                    response = get_home_page_version_1(auth, data)

                elif method == "postComment":
                    # auth = author_id
                    response = post_comment_version_1(auth, data)

                elif method == "getComments":
                    response = get_comments_version_1(data)

                elif method == "like":
                    # auth = author_id
                    response = like_or_unlike_post_version_1("like", auth, data)

                elif method == "unlike":
                    response = like_or_unlike_post_version_1("unlike", auth, data)

                elif method == "getLikes":
                    response = get_likes_version_1(data)

                elif method == "startToFollow":
                    # auth = following_id
                    response = follow_version_1("start", auth, data)

                elif method == "stopToFollow": # delete follower
                    # auth = following_id
                    response = follow_version_1("stop", auth, data)

                elif method == "deleteFollowing": # delete following
                    response = delete_following_version_1(auth, data)

                elif method == "determineFollowRequest":
                    response = determine_follow_request_version_1(auth, data)

                elif method == "getFollowers":
                    response = get_followers_version_1(auth, data)

                elif method == "getFollowings":
                    response = get_followings_version_1(auth, data)

                elif method == "getApplicantUsers":
                    response = get_applicant_users_version_1(auth, data)

                elif method == "blocking":
                    response = blocking_or_unblocking_following_version_1(auth, data)

                elif method == "getBlockedFollowings":
                    response = get_blocked_following_version_1(auth, data)

                elif method == "searchTags":
                    response = search_tags_version_1(data)

                elif method == "searchAccount":
                    response = search_account_version_1(data)

                elif method == "deletePicture":
                    response = delete_picture_version_1(data)

                serialized_output_obj = response.get("data")
                general_output_obj = OutputGeneral(method=method,
                                                   data=serialized_output_obj,
                                                   platform=platform,
                                                   lang_code=lang_code,
                                                   ver_api=ver_api)
                general_serialized = GeneralSerializerVersionOne(general_output_obj)
                response["data"] = general_serialized.data

                end_time = time.time()

                if end_time - start_time > 3:
                    logger.warning("getting response takes time more than 3 seconds")

                return Response(response)

        except Exception as e:
            logger.error("invalid input : " + str(e))
            response = manage_response(status_info="invalid input",
                                       data={})
            return Response(response)
