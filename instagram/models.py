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
    number_of_following = IntField(required=False, default=0)
    number_of_follower = IntField(required=False, default=0)
    number_of_posts = IntField(default=0)
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


class EmbeddedAuthor(EmbeddedDocument):
    username = StringField()
    picture = StringField()


# POST MODEL
class Comment(Document):
    _id = ObjectIdField()
    post_id = ObjectIdField()

    # Profile
    author = EmbeddedDocumentField(EmbeddedAuthor)
    comment_text = StringField()
    tags = ListField(StringField(max_length=30))
    date = IntField()

    meta = {
        'collection': 'comments'
    }


class Like(Document):
    _id = ObjectIdField()
    post_id = ObjectIdField()

    # Profile
    author = EmbeddedDocumentField(EmbeddedAuthor)

    meta = {
        'collection': 'likes'
    }


class Post(Document):
    _id = ObjectIdField()
    publisher = ObjectIdField()

    image = StringField()
    caption = StringField()
    tags = ListField(StringField(max_length=30))
    likes = IntField(default=0)
    published_date = IntField()

    meta = {
        'collection': 'posts'
    }


class HomePage(Document):
    _id = ObjectIdField()
    owner = ObjectIdField()
    # Post
    inclusive_posts = ListField(ObjectIdField())

    meta = {
        'collection': 'first_page'
    }
