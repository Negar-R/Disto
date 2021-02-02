from django.db import models
from mongoengine import *

# Create your models here.


# PROFILE MODEL
class Profile(Document):
    _id = ObjectIdField()
    username = StringField(required=True)
    first_name = StringField(required=False)
    last_name = StringField(required=False)
    picture = StringField(required=False)
    number_of_following = IntField(required=False)
    number_of_follower = IntField(required=False)
    date_of_join = IntField()

    meta = {
        'collection': 'profiles'
    }


class FollowingRelation(Document):
    _id = ObjectIdField()
    following = ObjectIdField()
    follower = ObjectIdField()

    meta = {
        'collection': 'following_relation'
    }


# POST MODEL
class Comment(Document):
    _id = ObjectIdField()
    comment_post = StringField()
    post_id = ObjectIdField()
    # Profile
    author = ObjectIdField()
    date = IntField()

    meta = {
        'collection': 'comments'
    }


class Like(Document):
    _id = ObjectIdField()
    # Profile
    author = ObjectIdField()
    post_id = ObjectIdField()

    meta = {
        'collection': 'likes'
    }


class Post(Document):
    _id = ObjectIdField()
    image = StringField()
    caption = StringField()
    tags = ListField(StringField(max_length=30))
    likes = IntField()
    comments = ListField(ObjectIdField())
    publisher = ObjectIdField()
    published_date = IntField()

    meta = {
        'collection': 'posts'
    }


class FirstPage(Document):
    _id = ObjectIdField()
    owner = ObjectIdField()
    # Post
    inclusive_pots = ListField(ObjectIdField())

    meta = {
        'collection': 'first_page'
    }
