import logging

from celery import shared_task

from instagram.models import Comment, Like, Post
from LikeInstaProject.mongo_client import mongo_client_obj
from LikeInstaProject.celery import app

logger = logging.getLogger(__name__)


@shared_task()
def remove_comments_of_blocked_user(blocked_username, post_ids):
    try:
        mongo_client_obj.remove_data(Comment,
                                     {"$and": [
                                        {'author.username': blocked_username},
                                        {'post_id': {"$in": post_ids}}
                                       ]})
        print("hale ;) ")
    except Exception as e:
        logger.error("remove_comments_of_blocked_user/celery : " + str(e))
        raise Exception


@shared_task()
def remove_likes_of_blocked_user(blocked_username, post_ids):
    try:
        target_posts = mongo_client_obj.fetch_data(Like,
                                                   {"$and": [
                                                       {'author.username': blocked_username},
                                                       {'post_id': {"$in": post_ids}}
                                                   ]})
        target_posts_ids = []
        for post in target_posts:
            target_posts_ids.append(post["post_id"])

        # decrease number of like
        decrease_like = mongo_client_obj.update_data(Post,
                                                     {'_id': {"$in": target_posts_ids}},
                                                     {"$inc": {'likes': -1}},
                                                     upsert=False,
                                                     multi=True)
        # remove likes object
        remove_like_list_of_blocked_user = mongo_client_obj.remove_data(Like,
                                                                        {'post_id': {"$in": target_posts_ids}})
        print("hale")
    except Exception as e:
        logger.error("remove_likes_of_blocked_user/celery : " + str(e))
        raise Exception
