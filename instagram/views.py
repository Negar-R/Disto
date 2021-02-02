from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from instagram.base_functions import manage_response
from instagram.methods_version_one import get_profile_version_1, create_profile_version_1, update_profile_version_1, \
    create_post_version_1, get_first_page, post_comment_version_1, like_post_version_1, follow_version_1, \
    get_followers_version_1
from instagram.validators import BodyStructureValidator



def check_body_of_request(data):
    try:
        BodyStructureValidator(**data)
    except ValidationError as e:
        response = manage_response(status=status.HTTP_200_OK,
                                   status_info="invalid input",
                                   data={})
        # return response
        return False
# Profile View
class ProfileAPIView(APIView):

    def post(self, request):

        valid = check_body_of_request(request.data)
        if valid is False:
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid input",
                                       data={})
            return response

        if request.data.get("ver_api") == 1:
            method = request.data.get("method")
            data = request.data.get("data")

            if method == "createProfile":
                response = create_profile_version_1(data)

            elif method == "updateProfile":
                profile_id = request.data["auth"]
                response = update_profile_version_1(profile_id, data)

            elif method == "getProfile":
                profile_id = request.data["data"]["profile_id"]
                response = get_profile_version_1(profile_id)

            return Response(response)


# Post View
class PostAPIView(APIView):

    def post(self, request):

        valid = check_body_of_request(request.data)
        if valid is False:
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid input",
                                       data={})
            return response

        if request.data.get("ver_api") == 1:
            method = request.data.get("method")
            data = request.data.get("data")
            publisher_id = request.data.get("auth")

            if method == "createPost":
                response = create_post_version_1(publisher_id, data)

            return Response(response)


class FirstPageAPIView(APIView):

    def post(self, request):

        valid = check_body_of_request(request.data)
        if valid is False:
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid input",
                                       data={})
            return response

        if request.data.get("ver_api") == 1:
            method = request.data.get("method")
            owner_id = request.data.get("auth")

            if method == "getFirstPage":
                response = get_first_page(owner_id)

            return Response(response)


class ReactOnPostAPIView(APIView):
    def post(self, request):

        valid = check_body_of_request(request.data)
        if valid is False:
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid input",
                                       data={})
            return response

        if request.data.get("ver_api") == 1:
            method = request.data.get("method")
            data = request.data.get("data")
            author_id = request.data.get("auth")

            if method == "postComment":
                response = post_comment_version_1(author_id, data)

            elif method == "like":
                response = like_post_version_1(author_id, data)

            return Response(response)


class FollowAPIView(APIView):
    def post(self, request):

        valid = check_body_of_request(request.data)
        if valid is False:
            response = manage_response(status=status.HTTP_200_OK,
                                       status_info="invalid input",
                                       data={})
            return response

        if request.data.get("ver_api") == 1:
            method = request.data.get("method")
            data = request.data.get("data")
            following_id = request.data.get("auth")

            if method == "startToFollow":
                response = follow_version_1("start", following_id, data)

            elif method == "stopToFollow":
                response = follow_version_1("stop", following_id, data)

            elif method == "getFollowers":
                response = get_followers_version_1(following_id)

            return Response(response)
