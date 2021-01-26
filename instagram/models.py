from django.db import models
from mongoengine import *

# Create your models here.


# PROFILE MODEL
class Profile(Document):
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
    comment_post = models.CharField(max_length=150)
    # Profile
    author = ObjectIdField()
    date = IntField()


class Post(Document):
    image = ImageField()
    caption = StringField()
    tags = ListField(StringField(max_length=30))
    likes = IntField()
    comments = ListField(ObjectIdField())
    publisher = ObjectIdField()
    published_date = IntField()


class FirstPage(Document):
    owner = ObjectIdField()
    # Post
    inclusive_pots = ListField(ObjectIdField())
