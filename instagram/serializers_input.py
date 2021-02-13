from pydantic.class_validators import Optional
from pydantic import BaseModel, validator, constr, Field
from instagram.models import Profile, FollowingRelation, Post
import re


class BodyStructureValidator(BaseModel):
    method: constr(min_length=2, strip_whitespace=True)
    data: dict
    auth: constr(min_length=24, max_length=24, strip_whitespace=True)
    ver_api: int


# PROFILE SERIALIZERS
class ProfileValidator(BaseModel):
    username: constr(min_length=5, max_length=100, strip_whitespace=True)
    first_name: Optional[str] = Field(None, min_length=2, max_length=50, extra={'strip_whitespace': True})
    last_name: Optional[str] = Field(None, min_length=2, max_length=50, extra={'strip_whitespace': True})
    picture: Optional[str] = Field(None, min_length=2, max_length=50, extra={'strip_whitespace': True})

    @validator('username', allow_reuse=True)
    def check_username_len_and_char(cls, v):
        if re.fullmatch(r'[A-Za-z0-9@#-_=]{5,}', v):
            return v
        else:
            raise ValueError('number of char is less than 5 or '
                             'invalid char, valid characters are [a-z] , [A-Z] , [0-9] , [@, #, -, _]')


class FollowingRelationValidator(BaseModel):
    follower: str


# POST SERIALIZERS
class PostValidator(BaseModel):
    image: constr(min_length=5, max_length=100, strip_whitespace=True)
    caption: Optional[str] = Field(None, min_length=2, max_length=50, extra={'strip_whitespace': True})


class CommentValidator(BaseModel):
    post_id: constr(min_length=24, max_length=24, strip_whitespace=True)
    comment_post: constr(min_length=5, max_length=100, strip_whitespace=True)


class LikeValidator(BaseModel):
    post_id: constr(min_length=24, max_length=24, strip_whitespace=True)


class PagePostsValidator(BaseModel):
    profile_id: constr(min_length=24, max_length=24, strip_whitespace=True)
