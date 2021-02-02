import time

from bson import ObjectId

from LikeInstaProject import mongo_client_obj
from instagram.models import Profile, Post, FollowingRelation, FirstPage, Comment, Like


def manage_response(status, status_info, data):
    response = {
        'status': status,
        'status_info': status_info,
        'data': data
    }
    return response


def create_profile(username, first_name, last_name, picture):
    data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'picture': picture,
        'date_of_join': time.time()
    }
    profile_obj = mongo_client_obj.insert_one_data(Profile, data)
    return profile_obj


def update_profile(profile_id, username, first_name, last_name, picture):
    data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'picture': picture,
    }
    profile_obj = mongo_client_obj.update_data(Profile,
                                               {'_id': ObjectId(profile_id)},
                                               {"$set": data},
                                               upsert=False)
    return profile_obj


def get_profile(profile_id):
    profile_obj = mongo_client_obj.fetch_one_data(Profile, '_id', ObjectId(profile_id))
    return profile_obj


def create_post(data):
    post_obj = mongo_client_obj.insert_one_data(Post, data)
    return post_obj


def publish_on_first_page(publisher_id, post_id):
    list_of_followings = mongo_client_obj.fetch_data(FollowingRelation, 'follower', ObjectId(publisher_id))
    for follow_relation in list_of_followings:
        following = follow_relation["following"]
        mongo_client_obj.update_data(FirstPage,
                                     {'owner': following},
                                     {"$push": {"inclusive_pots": ObjectId(post_id)}},
                                     upsert=True)

    return True


def get_first_page(owner_id):
    first_page_obj = mongo_client_obj.fetch_one_data(FirstPage, 'owner', ObjectId(owner_id))
    list_of_inclusive_posts = first_page_obj.inclusive_pots
    list_of_post_in_page = []
    for post_id in list_of_inclusive_posts:
        try:
            post_obj = mongo_client_obj.fetch_one_data(Post, '_id', post_id)
            post_dict = {
                "id": str(post_obj._id),
                "publisher": str(post_obj.publisher),
                "image": post_obj.image,
                "caption": post_obj.caption,
                "tags": post_obj.tags,
                "published_date": post_obj.published_date
            }
            list_of_post_in_page.append(post_dict)
        except Exception as e:
            pass

    return list_of_post_in_page


def post_comment(data):
    comment_obj = mongo_client_obj.insert_one_data(Comment, data)
    return comment_obj


def like_post(data):
    like_obj = mongo_client_obj.insert_one_data(Like, data)
    # increase the number of post's like
    post_id = data.get('post_id')
    mongo_client_obj.update_data(Post,
                                 {'_id': ObjectId(post_id)},
                                 {"$inc": {'likes': 1}},
                                 upsert=False)
    return like_obj


def start_to_follow(following_id, follower_id):
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
    return follower_obj, following_obj


def stop_to_follow(following_id, follower_id):
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

    return follower_obj, following_obj


def get_followers(following_id):
    list_of_followers = mongo_client_obj.fetch_data(FollowingRelation,
                                                    'following', ObjectId(following_id))
    list_of_followers_id = []
    for follower in list_of_followers:
        list_of_followers_id.append(follower.get("follower"))

    list_of_followers_profile = mongo_client_obj.fetch_data(Profile,
                                                            '_id', {"$in": list_of_followers_id})
    list_of_followers_username = []
    for follower_profile in list_of_followers_profile:
        list_of_followers_username.append(follower_profile["username"])

    return len(list_of_followers_username), list_of_followers_username
