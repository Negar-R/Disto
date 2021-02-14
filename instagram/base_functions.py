import time

from bson import ObjectId

from LikeInstaProject import mongo_client_obj
from LikeInstaProject.settings import per_page_limit
from instagram.commons import pagination
from instagram.models import Profile, Post, FollowingRelation, HomePage, Comment, Like
from instagram.out_models import OutputPost, EmbeddedUser, EmbeddedPost, EmbeddedComment, OutputProfile, \
    OutputHomePage, OutputFollowers, OutputFollowings, OutputPagePost, OutputComment, OutputLike


def manage_response(status, status_info, data):
    response = {
        'status': status,
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


def create_profile(username, first_name, last_name, picture):
    data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'picture': picture,
        'date_of_join': time.time()
    }
    profile_obj = mongo_client_obj.insert_one_data(Profile, data)
    profile_dict = make_dict_embedded_profile(profile_obj)
    output_profile_obj = OutputProfile(**profile_dict)
    return output_profile_obj


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
    profile_dict = make_dict_embedded_profile(profile_obj)
    output_profile_obj = OutputProfile(**profile_dict)
    return output_profile_obj


def get_profile(profile_id):
    profile_obj = mongo_client_obj.fetch_one_data(Profile, {'_id': ObjectId(profile_id)})
    profile_dict = make_dict_embedded_profile(profile_obj)
    output_profile_obj = OutputProfile(**profile_dict)
    return output_profile_obj


def create_post(data):
    post_obj = mongo_client_obj.insert_one_data(Post, data)
    profile_obj = mongo_client_obj.update_data(Profile,
                                               {"_id": post_obj.publisher},
                                               {"$inc": {"number_of_posts": 1}},
                                               upsert=False)
    publish_on_first_page(post_obj.publisher, post_obj._id)
    post_dict = make_dict_embedded_post(post_obj)
    profile_dict = make_dict_embedded_profile(profile_obj)
    output_create_post_obj = OutputPost(**{'publisher': profile_dict,
                                                 'post': post_dict})
    return output_create_post_obj


def publish_on_first_page(publisher_id, post_id):
    list_of_followings = mongo_client_obj.fetch_data(FollowingRelation, {'follower': publisher_id})
    for follow_relation in list_of_followings:
        following = follow_relation["following"]
        mongo_client_obj.update_data(HomePage,
                                     {'owner': following},
                                     {"$push": {"inclusive_posts": post_id}},
                                     upsert=True)

    return True


def get_page_post(profile_id):
    list_of_page_post_dict = mongo_client_obj.fetch_data(Post,
                                                         {'publisher': ObjectId(profile_id)},
                                                         per_page_limit=per_page_limit)
    list_of_post_in_page = []
    for post_dict in list_of_page_post_dict:
        post_obj = Post(**post_dict)
        changed_post_dict = make_dict_embedded_post(post_obj)
        list_of_post_in_page.append({'post': changed_post_dict})

    start_id, has_continue = pagination(list_of_page_post_dict, per_page_limit)
    output_page_post = OutputPagePost(start_id=start_id, has_continue=has_continue, posts=list_of_post_in_page)
    return output_page_post


def get_home_page(owner_id, start_id):
    first_page_obj = mongo_client_obj.fetch_one_data(HomePage, {'owner': ObjectId(owner_id)})

    list_of_inclusive_posts_id = first_page_obj.inclusive_posts
    if start_id is None:
        list_of_inclusive_posts_dict = mongo_client_obj.fetch_data(Post,
                                                                   {"$and": [
                                                                       {'_id': {"$in": list_of_inclusive_posts_id}},
                                                                   ]}, per_page_limit=per_page_limit)
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


def post_comment(post_id, comment_text, tags, author_id, date):
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


def get_comments(post_id):
    list_of_comments = mongo_client_obj.fetch_data(Comment, {'post_id': ObjectId(post_id)},
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


def get_likes(post_id):
    list_of_likes = mongo_client_obj.fetch_data(Like, {'post_id': ObjectId(post_id)},
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


def like_post(author_id, post_id):
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
    return True


def unlike_post(author_id, post_id):
    author_obj = mongo_client_obj.fetch_one_data(Profile, {'_id': ObjectId(author_id)})
    unlike_obj = mongo_client_obj.delete_one_data(Like, {"$and": [{'author': {'username': author_obj.username,
                                                                              'picture': author_obj.picture}},
                                                                  {'post_id': ObjectId(post_id)}]})
    mongo_client_obj.update_data(Post,
                                 {'_id': ObjectId(post_id)},
                                 {"$inc": {'likes': -1}},
                                 upsert=False)
    return True


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
    return True


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

    return True


def get_followers(following_id):
    list_of_followers = mongo_client_obj.fetch_data(FollowingRelation,
                                                    {'following': ObjectId(following_id)},
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


def get_followings(follower_id):
    list_of_followings = mongo_client_obj.fetch_data(FollowingRelation,
                                                     {'follower': ObjectId(follower_id)},
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
