from django.db import models
from mongoengine import *

# Create your models here.


# PROFILE MODEL
class Profile(Document):
    _id = ObjectIdField()
    username = StringField(required=True)
    first_name = StringField(required=False)
    last_name = StringField(required=False)
    picture = ImageField(required=False)
    number_of_following = IntField(required=False)
    number_of_follower = IntField(required=False)
    date_of_join = IntField()


class FollowingRelation(Document):
    following = ObjectIdField()
    follower = ObjectIdField()


# POST MODEL
class Comment(Document):
    _id = ObjectIdField()
    comment_post = models.CharField(max_length=150)
    post_id = ObjectIdField()
    # Profile
    author = ObjectIdField()
    date = IntField()


class Like(Document):
    # Profile
    author = ObjectIdField()
    post_id = ObjectIdField()


class Post(Document):
    _id = ObjectIdField()
    image = ImageField()
    caption = StringField()
    tags = ListField(StringField(max_length=30))
    likes = IntField()
    comments = ListField(ObjectIdField())
    publisher = ObjectIdField()
    published_date = IntField()


class FirstPage(Document):
    _id = ObjectIdField()
    owner = ObjectIdField()
    # Post
    inclusive_pots = ListField(ObjectIdField())
