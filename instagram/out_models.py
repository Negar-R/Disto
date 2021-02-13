from mongoengine import *


class EmbeddedUser(EmbeddedDocument):
    username = StringField(required=True)
    first_name = StringField(required=False)
    last_name = StringField(required=False)
    picture = StringField(required=False)
    number_of_following = IntField(required=False, default=0)
    number_of_follower = IntField(required=False, default=0)
    number_of_posts = IntField(default=0)
    date_of_join = IntField()


class EmbeddedComment(EmbeddedDocument):
    author = EmbeddedDocumentField(EmbeddedUser)
    comment_text = StringField()
    date = IntField()


class EmbeddedLike(EmbeddedDocument):
    author = EmbeddedDocumentField(EmbeddedUser)


class EmbeddedPost(EmbeddedDocument):
    image = StringField()
    caption = StringField()
    number_of_likes = IntField(default=0)
    likes = IntField()
    # comments = ListField(EmbeddedDocumentField(EmbeddedComment))


class OutputCreatePost(EmbeddedDocument):
    publisher = EmbeddedDocumentField(EmbeddedUser)
    post = EmbeddedDocumentField(EmbeddedPost)


class EmbeddedPagePost(EmbeddedDocument):
    post = EmbeddedDocumentField(EmbeddedPost)


class OutputGeneral(Document):
    platform_type = {
        'IOS': 'IOS',
        'Android': 'Android',
        'Desktop': 'Desktop',
        'Web': 'Web'
    }

    method = StringField(max_length=50)
    data = DictField()
    platform = StringField(min_length=3, required=True)
    lang_code = StringField(min_length=2, max_length=2)
    ver_api = IntField()


class OutputProfile(Document):
    username = StringField(required=True)
    first_name = StringField(required=False)
    last_name = StringField(required=False)
    picture = StringField(required=False)
    number_of_following = IntField(required=False, default=0)
    number_of_follower = IntField(required=False, default=0)
    number_of_posts = IntField(default=0)
    date_of_join = IntField()


class OutputPagePost(Document):
    posts = EmbeddedDocumentListField(EmbeddedPagePost)


class OutputHomePage(Document):
    posts = ListField(EmbeddedDocumentField(OutputCreatePost))


class OutputComment(Document):
    comments = ListField(EmbeddedDocumentField(EmbeddedComment))


class OutputLike(Document):
    likes = EmbeddedDocumentListField(EmbeddedLike)


class OutputFollowers(Document):
    followers = ListField(EmbeddedDocumentField(EmbeddedUser))


class OutputFollowings(Document):
    followings = ListField(EmbeddedDocumentField(EmbeddedUser))

