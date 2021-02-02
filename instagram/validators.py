from rest_framework_mongoengine.serializers import DocumentSerializer
from pydantic import BaseModel, validator, constr
from instagram.models import Profile, FollowingRelation, Post
import re


# PROFILE SERIALIZERS
# class ProfileSerializer(DocumentSerializer):
#     class Meta:
#         model = Profile
#         fields = ('username', 'last_name', 'first_name', 'picture')

class ProfileBodyRequestValidator(BaseModel):
    method: str
    new_data: dict
    get_info: dict


class ProfileValidator(BaseModel):
    username: str
    first_name: str = None
    last_name: str = None
    picture: str = None

    @validator('username', allow_reuse=True)
    def check_username_len_and_char(cls, v):
        if re.fullmatch(r'[A-Za-z0-9@#-_=]{5,}', v):
            return v
        else:
            raise ValueError('number of char is less than 5 or '
                             'invalid char, valid characters are [a-z] , [A-Z] , [0-9] , [@, #, -, _]')


class FollowingRelationValidator(BaseModel):
    following: str
    follower: str

    @validator('follower')
    def check_not_to_same(cls, v, values):
        if v == values["following"]:
            raise ValueError("should not be same")
        else:
            return v


class FollowingRelationBodyValidator(BaseModel):
    method: str
    data: dict


# class FollowingRelationSerializer(DocumentSerializer):
#     class Meta:
#         model = FollowingRelation
#         fields = ('follower', )


# POST SERIALIZERS
# class PostSerializer(DocumentSerializer):
#     class Meta:
#         model = Post
#         exclude = ('likes', 'comments', 'published_date')


class PostValidator(BaseModel):
    caption: constr(min_length=5, max_length=100, strip_whitespace=True)
    image: str = None
    publisher: str


class ReactionKindValidator(BaseModel):
    data: dict = None
    reaction_kind: str

    @validator('reaction_kind')
    def check_comment_body(cls, v, values, **kwargs):
        if v == "comment" and values["data"] is None:
            raise ValueError('comment should have comment_post and author_id')
        else:
            return v
