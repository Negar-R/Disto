import os
import time
import logging

from bson import ObjectId

from rest_framework import status

from LikeInstaProject import mongo_client_obj
from LikeInstaProject.settings import per_page_limit
from instagram.commons import pagination
from instagram.tasks import remove_comments_of_blocked_user, remove_likes_of_blocked_user
from instagram.models import Profile, Post, FollowingRelation, HomePage, Comment, Like, FollowRequest, UploadedImage
from instagram.out_models import OutputPost, EmbeddedUser, EmbeddedPost, EmbeddedComment, OutputProfile, \
    OutputHomePage, OutputFollowers, OutputFollowings, OutputPagePost, OutputComment, OutputLike


logger = logging.getLogger(__name__)


def manage_response(status_info, data):
    response = {
        'status': status.HTTP_200_OK,
        'status_info': status_info,
        'data': data
    }
    return response


def make_dict_embedded_post(post_obj):
    post_dict = {
        "image": post_obj.image,
        "caption": post_obj.caption,
        "likes": post_obj.likes
    }
    return post_dict


def make_dict_embedded_profile(profile_obj):
    profile_dict = {
        "username": profile_obj.username,
        "first_name": profile_obj.first_name,
        "last_name": profile_obj.last_name,
        "picture": profile_obj.picture,
        "private": profile_obj.private,
        "number_of_following": profile_obj.number_of_following,
        "number_of_follower": profile_obj.number_of_follower,
        "number_of_posts": profile_obj.number_of_posts,
        "date_of_join": profile_obj.date_of_join
    }
    return profile_dict


def make_dict_embedded_comment(author_username, author_picture, comment_text, date):
    comment_dict = {
        "author": {
            "username": author_username,
            "picture": author_picture
        },
        "comment_text": comment_text,
        "date": date
    }
    return comment_dict


def create_profile(username, first_name, last_name, picture, picture_id, private):
    try:
        data = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'picture': picture,
            'picture_id': ObjectId(picture_id),
            'private': private,
            'date_of_join': time.time()
        }
        profile_obj = mongo_client_obj.insert_one_data(Profile, data)
        profile_dict = make_dict_embedded_profile(profile_obj)
        output_profile_obj = OutputProfile(**profile_dict)
        return output_profile_obj
    except Exception as e:
        logger.error("create_profile/base : " + str(e))
        raise Exception(str(e))


def update_profile(profile_id, username, first_name, last_name, picture, picture_id, private):
    try:
        data = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'picture': picture,
            'picture_id': ObjectId(picture_id),
            'private': private
        }
        old_profile_obj = mongo_client_obj.fetch_one_data(Profile,
                                                          {'_id': ObjectId(profile_id)})
        # delete previous picture
        if old_profile_obj.picture_id != picture_id:
            delete_picture(old_profile_obj.picture_id)
        # update whole object
        profile_obj = mongo_client_obj.update_data(Profile,
                                                   {'_id': ObjectId(profile_id)},
                                                   {"$set": data},
                                                   upsert=False)
        profile_dict = make_dict_embedded_profile(profile_obj)
        output_profile_obj = OutputProfile(**profile_dict)
        return output_profile_obj
    except Exception as e:
        logger.error("update_profile/base : " + str(e))
        raise Exception(str(e))


def get_profile(profile_id):
    try:
        profile_obj = mongo_client_obj.fetch_one_data(Profile, {'_id': ObjectId(profile_id)})
        profile_dict = make_dict_embedded_profile(profile_obj)
        output_profile_obj = OutputProfile(**profile_dict)
        return output_profile_obj
    except Exception as e:
        logger.error("get_profile/base : " + str(e))
        raise Exception(str(e))


def delete_picture(image_id):
    try:
        image_obj = mongo_client_obj.fetch_one_data(UploadedImage,
                                                    {'_id': ObjectId(image_id)})
        os.remove(image_obj.image_address)
        mongo_client_obj.delete_one_data(UploadedImage,
                                         {'_id': ObjectId(image_id)})
        return "deleted"
    except Exception as e:
        logger.error("delete_picture/base : " + str(e))
        raise Exception(str(e))


def create_post(data):
    try:
        post_obj = mongo_client_obj.insert_one_data(Post, data)
        profile_obj = mongo_client_obj.update_data(Profile,
                                                   {"_id": post_obj.publisher},
                                                   {"$inc": {"number_of_posts": 1}},
                                                   upsert=False)
        publish_on_home_page(post_obj.publisher, post_obj._id)
        post_dict = make_dict_embedded_post(post_obj)
        profile_dict = make_dict_embedded_profile(profile_obj)
        output_create_post_obj = OutputPost(**{'publisher': profile_dict,
                                               'post': post_dict})
        return output_create_post_obj
    except Exception as e:
        logger.error("create_post/base :" + str(e))
        raise Exception(str(e))


def publish_on_home_page(publisher_id, post_id):
    try:
        list_of_followings = mongo_client_obj.fetch_data(FollowingRelation, {'follower': publisher_id})
        for follow_relation in list_of_followings:
            following = follow_relation["following"]
            mongo_client_obj.update_data(HomePage,
                                         {'owner': following},
                                         {"$push": {"inclusive_posts": post_id}},
                                         upsert=True)
        return True
    except Exception as e:
        logger.error("publish_on_home_page/base : " + str(e))
        raise Exception(str(e))


def get_page_post(profile_id, start_id):
    try:
        if start_id is None:
            list_of_page_post_dict = mongo_client_obj.fetch_data(Post,
                                                                 {'publisher': ObjectId(profile_id)},
                                                                 per_page_limit=per_page_limit)
        else:
            list_of_page_post_dict = mongo_client_obj.fetch_data(Post,
                                                                 {"$and": [
                                                                     {'_id': {"$lt": ObjectId(start_id)}},
                                                                     {'publisher': ObjectId(profile_id)}]},
                                                                 per_page_limit=per_page_limit)

        list_of_post_in_page = []
        for post_dict in list_of_page_post_dict:
            post_obj = Post(**post_dict)
            changed_post_dict = make_dict_embedded_post(post_obj)
            list_of_post_in_page.append({'post': changed_post_dict})

        start_id, has_continue = pagination(list_of_page_post_dict, per_page_limit)
        output_page_post = OutputPost(start_id=start_id, has_continue=has_continue, posts=list_of_post_in_page)
        return output_page_post
    except Exception as e:
        logger.error("get_page_post/base : " + str(e))
        raise Exception(str(e))


def get_home_page(owner_id, start_id):
    try:
        first_page_obj = mongo_client_obj.fetch_one_data(HomePage, {'owner': ObjectId(owner_id)})

        list_of_inclusive_posts_id = first_page_obj.inclusive_posts
        if start_id is None:
            list_of_inclusive_posts_dict = mongo_client_obj.fetch_data(Post,
                                                                       {'_id': {"$in": list_of_inclusive_posts_id}},
                                                                       per_page_limit=per_page_limit)
        else:
            list_of_inclusive_posts_dict = mongo_client_obj.fetch_data(Post,
                                                                       {"$and": [
                                                                           {'_id': {"$in": list_of_inclusive_posts_id}},
                                                                           {'_id': {"$lt": ObjectId(start_id)}}
                                                                       ]}, per_page_limit=per_page_limit)
        publisher_id_list = list()
        for post in list_of_inclusive_posts_dict:
            publisher_id_list.append(post.get("publisher"))
        list_of_inclusive_publishers_dict = mongo_client_obj.fetch_data(Profile,
                                                                        {'_id': {"$in": publisher_id_list}})
        list_of_post_in_page = []
        for post_dict in list_of_inclusive_posts_dict:
            for profile_dict in list_of_inclusive_publishers_dict:
                if post_dict.get("publisher") == profile_dict.get("_id"):
                    publisher_obj = Profile(**profile_dict)
                    publisher_dict = make_dict_embedded_profile(publisher_obj)
                    post_obj = Post(**post_dict)
                    changed_post_dict = make_dict_embedded_post(post_obj)
                    list_of_post_in_page.append({'publisher': publisher_dict,
                                                 'post': changed_post_dict})
                    break

        start_id, has_continue = pagination(list_of_inclusive_posts_dict, per_page_limit)
        output_first_page = OutputHomePage(start_id=start_id, has_continue=has_continue, posts=list_of_post_in_page)
        return output_first_page
    except Exception as e:
        logger.error("get_home_page/base : " + str(e))
        raise Exception(str(e))


def post_comment(post_id, comment_text, tags, author_id, date):
    try:
        author_obj = mongo_client_obj.fetch_one_data(Profile, {'_id': ObjectId(author_id)})
        data = {
            'post_id': post_id,
            'comment_text': comment_text,
            'author': {
                'username': author_obj.username,
                'picture': author_obj.picture
            },
            'tags': tags,
            'date': date
        }
        comment_obj = mongo_client_obj.insert_one_data(Comment, data)
        comment_dict = make_dict_embedded_comment(author_obj.username, author_obj.picture,
                                                  comment_obj.comment_text, comment_obj.date)
        output_comment = EmbeddedComment(**comment_dict)
        return output_comment
    except Exception as e:
        logger.error("post_comment/base : " + str(e))
        raise Exception(str(e))


def get_comments(post_id, start_id):
    try:
        if start_id is None:
            list_of_comments = mongo_client_obj.fetch_data(Comment, {'post_id': ObjectId(post_id)},
                                                           per_page_limit=per_page_limit)
        else:
            list_of_comments = mongo_client_obj.fetch_data(Comment,
                                                           {"$and": [
                                                               {'_id': {"$lt": ObjectId(start_id)}},
                                                               {'post_id': ObjectId(post_id)}]},
                                                           per_page_limit=per_page_limit)

        list_of_comments_dict = []
        for comment in list_of_comments:
            author_username = comment["author"]["username"]
            author_picture = comment["author"]["picture"]
            comment_dict = make_dict_embedded_comment(author_username,
                                                      author_picture,
                                                      comment.get("comment_text"),
                                                      comment.get("date"))

            list_of_comments_dict.append(comment_dict)

        start_id, has_continue = pagination(list_of_comments, per_page_limit)
        output_comment_obj = OutputComment(start_id=start_id, has_continue=has_continue, comments=list_of_comments_dict)
        return output_comment_obj
    except Exception as e:
        logger.error("get_comments/base" + str(e))
        raise Exception(str(e))


def get_likes(post_id, start_id):
    try:
        if start_id is None:
            list_of_likes = mongo_client_obj.fetch_data(Like, {'post_id': ObjectId(post_id)},
                                                        per_page_limit=per_page_limit)
        else:
            list_of_likes = mongo_client_obj.fetch_data(Like,
                                                        {"$and": [
                                                            {'_id': {"$lt": ObjectId(start_id)}},
                                                            {'post_id': ObjectId(post_id)}]},
                                                        per_page_limit=per_page_limit)
        list_of_likes_dict = []
        for like in list_of_likes:
            author_username = like["author"]["username"]
            author_picture = like["author"]["picture"]
            list_of_likes_dict.append({'author': {
                                                    'username': author_username,
                                                    'picture': author_picture}})

        start_id, has_continue = pagination(list_of_likes, per_page_limit)
        output_like_obj = OutputLike(start_id=start_id, has_continue=has_continue, likes=list_of_likes_dict)
        return output_like_obj
    except Exception as e:
        logger.error("get_likes/base" + str(e))
        raise Exception(str(e))


def like_post(author_id, post_id):
    try:
        author_obj = mongo_client_obj.fetch_one_data(Profile, {'_id': ObjectId(author_id)})
        like_obj = mongo_client_obj.insert_one_data(Like, {'author': {
                                                                'username': author_obj.username,
                                                                'picture': author_obj.picture},
                                                           'post_id': ObjectId(post_id)})
        # increase the number of post's like
        mongo_client_obj.update_data(Post,
                                     {'_id': ObjectId(post_id)},
                                     {"$inc": {'likes': 1}},
                                     upsert=False)
        return "like"
    except Exception as e:
        logger.error("like_post/base" + str(e))
        raise Exception(str(e))


def unlike_post(author_id, post_id):
    try:
        author_obj = mongo_client_obj.fetch_one_data(Profile, {'_id': ObjectId(author_id)})
        unlike_obj = mongo_client_obj.delete_one_data(Like, {"$and": [{'author': {'username': author_obj.username,
                                                                                  'picture': author_obj.picture}},
                                                                      {'post_id': ObjectId(post_id)}]})
        mongo_client_obj.update_data(Post,
                                     {'_id': ObjectId(post_id)},
                                     {"$inc": {'likes': -1}},
                                     upsert=False)
        return "unlike"
    except Exception as e:
        logger.error("unlike_post/base" + str(e))
        raise Exception(str(e))


def request_to_follow(applicant_user, requested_user):
    try:
        request_obj = mongo_client_obj.insert_one_data(FollowRequest,
                                                       {'applicant_user': applicant_user,
                                                        'requested_user': requested_user})
        return "requested"
    except Exception as e:
        logger.error("request_to_follow/base : " + str(e))
        raise Exception(str(e))


def follow(following_id, follower_id):
    following_id = ObjectId(following_id)
    follower_id = ObjectId(follower_id)

    mongo_client_obj.insert_one_data(FollowingRelation,
                                     {'following': following_id,
                                      'follower': follower_id})
    # increase the number of follower and following
    follower_obj = mongo_client_obj.update_data(Profile,
                                                {'_id': following_id},
                                                {"$inc": {'number_of_follower': 1}},
                                                upsert=False)
    following_obj = mongo_client_obj.update_data(Profile,
                                                 {'_id': follower_id},
                                                 {"$inc": {'number_of_following': 1}},
                                                 upsert=False)
    return "followed"


def start_to_follow(following_id, follower_id):
    try:
        following_id = ObjectId(following_id)
        follower_id = ObjectId(follower_id)

        follower_profile = mongo_client_obj.fetch_one_data(Profile,
                                                           {'_id': follower_id})
        if follower_profile.private:
            return request_to_follow(applicant_user=following_id, requested_user=follower_id)
        else:
            return follow(following_id, follower_id)

    except Exception as e:
        logger.error("start_to_follow/base : " + str(e))
        raise Exception(str(e))


def stop_to_follow(following_id, follower_id):
    try:
        following_id = ObjectId(following_id)
        follower_id = ObjectId(follower_id)

        mongo_client_obj.delete_one_data(FollowingRelation,
                                         {'following': following_id,
                                          'follower': follower_id})
        # decrease the number of followers and followings
        follower_obj = mongo_client_obj.update_data(Profile,
                                                    {'_id': following_id},
                                                    {"$inc": {'number_of_follower': -1}},
                                                    upsert=False)
        following_obj = mongo_client_obj.update_data(Profile,
                                                     {'_id': follower_id},
                                                     {"$inc": {'number_of_following': -1}},
                                                     upsert=False)

        return "stop"
    except Exception as e:
        logger.error("stop_to_follow/base : " + str(e))
        raise Exception(str(e))


def delete_following(auth, following_id):
    try:
        auth = ObjectId(auth)
        following_id = ObjectId(following_id)

        deleted_count = mongo_client_obj.delete_one_data(FollowingRelation,
                                                         {'following': following_id,
                                                          'follower': auth})

        following_obj = mongo_client_obj.update_data(Profile,
                                                     {'_id': auth},
                                                     {"$inc": {'number_of_following': -1}},
                                                     upsert=False)

        follower_obj = mongo_client_obj.update_data(Profile,
                                                    {'_id': following_id},
                                                    {"$inc": {'number_of_follower': -1}},
                                                    upsert=False)
        return "stop"

    except Exception as e:
        logger.error("delete_following/base : " + str(e))
        raise Exception(str(e))


def determine_follow_request(action, auth, following_id):
    try:
        request_obj = mongo_client_obj.delete_one_data(FollowRequest,
                                                       {'requested_user': ObjectId(auth),
                                                        'applicant_user': ObjectId(following_id)})
        if action == "accept":
            follow(following_id=following_id, follower_id=auth)
            return "accept"
        else:
            return "reject"

    except Exception as e:
        logger.error("determine_follow_request/base : " + str(e))
        raise Exception(str(e))


def show_followers(user_id, start_id):
    try:
        if start_id is None:
            list_of_followers = mongo_client_obj.fetch_data(FollowingRelation,
                                                            {'following': ObjectId(user_id)},
                                                            per_page_limit=per_page_limit)
        else:
            list_of_followers = mongo_client_obj.fetch_data(FollowingRelation,
                                                            {"$and": [
                                                                {'_id': {"$lt": ObjectId(start_id)}},
                                                                {'following': ObjectId(user_id)}]},
                                                            per_page_limit=per_page_limit)
        list_of_followers_id = []
        for follower in list_of_followers:
            list_of_followers_id.append(follower.get("follower"))

        list_of_followers_profile = mongo_client_obj.fetch_data(Profile,
                                                                {'_id': {"$in": list_of_followers_id}})
        followers = []
        for follower_profile in list_of_followers_profile:
            profile_obj = Profile(**follower_profile)
            profile_dict = make_dict_embedded_profile(profile_obj)
            followers.append(profile_dict)

        start_id, has_continue = pagination(list_of_followers, per_page_limit)
        output_followers_obj = OutputFollowers(start_id=start_id, has_continue=has_continue, followers=followers)
        return output_followers_obj

    except Exception as e:
        logger.error("show_followers/base : " + str(e))
        raise Exception(str(e))


def get_followers(auth, user_id, start_id):
    try:
        profile_of_user = mongo_client_obj.fetch_one_data(Profile,
                                                          {'_id': ObjectId(user_id)})
        if profile_of_user.private:
            existence_of_follow_relation = mongo_client_obj.fetch_one_data(FollowingRelation,
                                                                           {"$and": [
                                                                               {'following': ObjectId(auth)},
                                                                               {'follower': ObjectId(user_id)}
                                                                           ]})
            if existence_of_follow_relation == "Does Not Exist":
                return "not allowed"
            else:
                return show_followers(user_id, start_id)
        else:
            return show_followers(user_id, start_id)
    except Exception as e:
        logger.error("get_followers/base : " + str(e))
        raise Exception(str(e))


def show_followings(user_id, start_id):
    try:
        if start_id is None:
            list_of_followings = mongo_client_obj.fetch_data(FollowingRelation,
                                                             {'follower': ObjectId(user_id)},
                                                             per_page_limit=per_page_limit)
        else:
            list_of_followings = mongo_client_obj.fetch_data(FollowingRelation,
                                                             {"$and": [
                                                                 {'_id': {"$lt": ObjectId(start_id)}},
                                                                 {'follower': ObjectId(user_id)}]},
                                                             per_page_limit=per_page_limit)
        list_of_followings_id = []
        for following in list_of_followings:
            list_of_followings_id.append(following.get("following"))
        list_of_followings_profile = mongo_client_obj.fetch_data(Profile,
                                                                 {'_id': {"$in": list_of_followings_id}})

        followings = []
        for following_profile in list_of_followings_profile:
            profile_obj = Profile(**following_profile)
            profile_dict = make_dict_embedded_profile(profile_obj)
            followings.append(profile_dict)

        start_id, has_continue = pagination(list_of_followings, per_page_limit)
        output_followings_obj = OutputFollowings(start_id=start_id, has_continue=has_continue, followings=followings)
        return output_followings_obj

    except Exception as e:
        logger.error("show_followings/base : " + str(e))
        raise Exception(str(e))


def get_followings(auth, user_id, start_id):
    try:
        profile_of_user = mongo_client_obj.fetch_one_data(Profile,
                                                          {'_id': ObjectId(user_id)})
        if profile_of_user.private:
            existence_of_follow_relation = mongo_client_obj.fetch_one_data(FollowingRelation,
                                                                           {"$and": [
                                                                               {'following': ObjectId(auth)},
                                                                               {'follower': ObjectId(user_id)}
                                                                           ]})
            if existence_of_follow_relation == "Does Not Exist":
                return "not allowed"
            else:
                return show_followings(user_id, start_id)
        else:
            return show_followings(user_id, start_id)
    except Exception as e:
        logger.error("get_followings/base : " + str(e))
        raise Exception(str(e))


def get_applicant_users(auth, start_id):
    try:
        if start_id is None:
            list_of_follow_request = mongo_client_obj.fetch_data(FollowRequest,
                                                                 {'requested_user': ObjectId(auth)},
                                                                 per_page_limit=per_page_limit)
        else:
            list_of_follow_request = mongo_client_obj.fetch_data(FollowRequest,
                                                                 {"$and": [
                                                                     {'_id': {"$lt": ObjectId(start_id)}},
                                                                     {'requested_user': ObjectId(auth)}
                                                                 ]},
                                                                 per_page_limit=per_page_limit)
        list_of_applicant_user_id = []
        for applicant_dict in list_of_follow_request:
            list_of_applicant_user_id.append(applicant_dict['applicant_user'])

        list_of_applicant_profile = mongo_client_obj.fetch_data(Profile,
                                                                {'_id': {"$in": list_of_applicant_user_id}})
        applicant_users = []
        for applicant_user in list_of_applicant_profile:
            applicant_user_obj = Profile(**applicant_user)
            profile_dict = make_dict_embedded_profile(applicant_user_obj)
            applicant_users.append(profile_dict)

        start_id, has_continue = pagination(list_of_follow_request, per_page_limit)
        output_applicant_users_obj = OutputFollowers(start_id=start_id, has_continue=has_continue,
                                                     followers=applicant_users)
        return output_applicant_users_obj

    except Exception as e:
        logger.error("get_applicant_users/base : " + str(e))
        raise Exception(str(e))


# TODO: write a validator for it
def block_or_unblock_following(action, auth, following_id):
    if action == "block":
        try:
            # blocking = mongo_client_obj.update_data(FollowingRelation,
            #                                         {"$and": [
            #                                             {'following': ObjectId(following_id)},
            #                                             {'follower': ObjectId(auth)}]},
            #                                         {"$set": {'block': True}},
            #                                         upsert=False)

            # find profile of blocked user
            blocked_profile = mongo_client_obj.fetch_one_data(Profile,
                                                              {'_id': ObjectId(following_id)})
            blocked_username = blocked_profile.username

            post_list_of_blocker = mongo_client_obj.fetch_data(Post,
                                                               {'publisher': ObjectId(auth)})
            post_ids = []
            for post in post_list_of_blocker:
                post_ids.append(post["_id"])
            print("post:ids : ", post_ids)

            # TODO : make the error correct
            remove_comments_of_blocked_user.delay(blocked_username=blocked_username, post_ids=2)
            # remove_likes_of_blocked_user.delay(blocked_username, post_ids)

            return "blocked"

        except Exception as e:
            logger.error("block/base : " + str(e))
            raise Exception(str(e))

    elif action == "unblock":
        try:
            blocking = mongo_client_obj.update_data(FollowingRelation,
                                                    {"$and": [
                                                        {'following': ObjectId(following_id)},
                                                        {'follower': ObjectId(auth)}]},
                                                    {"$set": {'block': False}},
                                                    upsert=False)
            return "unblocked"

        except Exception as e:
            logger.error("unblock/base : " + str(e))
            raise Exception(str(e))


def get_blocked_following(auth, start_id):
    try:
        if start_id is None:
            list_of_blocked_following = mongo_client_obj.fetch_data(FollowingRelation,
                                                                    {"$and": [
                                                                        {'follower': ObjectId(auth)},
                                                                        {'block': True}]},
                                                                    per_page_limit=per_page_limit)
        else:
            list_of_blocked_following = mongo_client_obj.fetch_data(FollowingRelation,
                                                                    {"$and": [
                                                                        {'_id': {"$lt": ObjectId(start_id)}},
                                                                        {'follower': ObjectId(auth)},
                                                                        {'block': True}]},
                                                                    per_page_limit=per_page_limit)
        list_of_blocked_followings_id = []
        for blocked_following in list_of_blocked_following:
            list_of_blocked_followings_id.append(blocked_following.get("following"))

        list_of_blocked_followings_profile = mongo_client_obj.fetch_data(Profile,
                                                                 {'_id': {"$in": list_of_blocked_followings_id}})

        blocked_followings = []
        for blocked_following_profile in list_of_blocked_followings_profile:
            profile_obj = Profile(**blocked_following_profile)
            profile_dict = make_dict_embedded_profile(profile_obj)
            blocked_followings.append(profile_dict)

        start_id, has_continue = pagination(list_of_blocked_following, per_page_limit)
        output_blocked_followings_obj = OutputFollowings(start_id=start_id, has_continue=has_continue,
                                                         followings=blocked_followings)
        return output_blocked_followings_obj

    except Exception as e:
        logger.error("get_blocked_following/base : " + str(e))
        raise Exception(str(e))


def search_tags(tag, start_id):
    try:
        if tag[0] == '#':
            tag = tag[1:]

        if start_id is None:
            list_of_founded_post_dict = mongo_client_obj.fetch_data(Post,
                                                                    {'tags': {"$regex": "^" + tag + "*"}},
                                                                    per_page_limit=per_page_limit)
        else:
            list_of_founded_post_dict = mongo_client_obj.fetch_data(Post,
                                                                    {"$and": [
                                                                        {'_id': {"$lt": ObjectId(start_id)}},
                                                                        {'tags': {"$regex": "^" + tag + "*"}}]},
                                                                    per_page_limit=per_page_limit)
        list_of_post = []
        for post_dict in list_of_founded_post_dict:
            post_obj = Post(**post_dict)
            founded_post_dict = make_dict_embedded_post(post_obj)
            list_of_post.append({'post': founded_post_dict})

        start_id, has_continue = pagination(list_of_founded_post_dict, per_page_limit)
        output_founded_post = OutputPagePost(start_id=start_id, has_continue=has_continue, posts=list_of_post)
        return output_founded_post

    except Exception as e:
        logger.error("search_tags/base : " + str(e))
        raise Exception(str(e))


def search_account(username, start_id):
    try:
        if start_id is None:
            list_of_founded_profile = mongo_client_obj.fetch_data(Profile,
                                                                  {'username': {"$regex": "^" + username + "*"}},
                                                                  per_page_limit=per_page_limit)
        else:
            list_of_founded_profile = mongo_client_obj.fetch_data(Profile,
                                                                  {"$and": [
                                                                      {'_id': {"$lt": ObjectId(start_id)}},
                                                                      {'username': {"$regex": "^" + username + "*"}}
                                                                  ]}, per_page_limit=per_page_limit)

        profiles = []
        for profile_dict in list_of_founded_profile:
            profile_obj = Profile(**profile_dict)
            founded_profile_dict = make_dict_embedded_profile(profile_obj)
            profiles.append(founded_profile_dict)

        start_id, has_continue = pagination(list_of_founded_profile, per_page_limit)
        output_founded_profile_obj = OutputFollowers(start_id=start_id, has_continue=has_continue, followers=profiles)
        return output_founded_profile_obj

    except Exception as e:
        logger.error("search_account/base : " + str(e))
        raise Exception(str(e))
