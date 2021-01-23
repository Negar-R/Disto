from profiles.models import Profile
from datetime import datetime
from django.db import models
from mongoengine import *

# Create your models here.


class Comment(Document):
    comment_post = models.CharField(max_length=150)
    author = ListField(ReferenceField(Profile))
    date = DateTimeField(default=datetime.now())


class Post(Document):
    # image = ImageField()
    image_caption = StringField()
    # image_likes = ListField(ReferenceField(Profile))
    # comment = ListField(ReferenceField(Comment))
    tags = ListField(StringField(max_length=30))
    published_date = DateTimeField(default=datetime.now())
