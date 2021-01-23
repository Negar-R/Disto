from datetime import datetime
from django.db import models
from mongoengine import *

# Create your models here.


class Profile(Document):
    username = StringField(required=True)
    first_name = StringField(required=False)
    last_name = StringField(required=False)
    picture = ImageField(required=False)
    # TODO : think more about this two fields.
    # following =
    # follower =
    date_of_join = DateField(default=datetime.now())
