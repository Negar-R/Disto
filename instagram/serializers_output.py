from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer


from instagram.out_models import OutputCreatePost, OutputProfile, EmbeddedUser, EmbeddedPost, OutputHomePage, \
    OutputFollowers, OutputFollowings, EmbeddedComment, EmbeddedLike, OutputPagePost, EmbeddedPagePost, OutputComment, \
    OutputLike, OutputGeneral


class EmbeddedUserSerializerVersionOne(DocumentSerializer):
    class Meta:
        model = EmbeddedUser
        fields = ('username', 'picture')


class EmbeddedCommentsSerializerVersionOne(DocumentSerializer):
    author = EmbeddedUserSerializerVersionOne(many=False)

    class Meta:
        model = EmbeddedComment
        fields = ('author', 'comment_text', 'date')


class EmbeddedLikeSerializerVersionOne(DocumentSerializer):
    author = EmbeddedUserSerializerVersionOne(many=False)

    class Meta:
        model = EmbeddedLike
        fields = ('author',)


class EmbeddedPostSerializerVersionOne(DocumentSerializer):
    # comments = EmbeddedCommentsSerializerVersionOne(many=True)
    # likes = EmbeddedLikeSerializerVersionOne(many=True)

    class Meta:
        model = EmbeddedPost
        fields = ('image', 'caption', 'number_of_likes')


class EmbeddedPagePostSerializerVersionOne(DocumentSerializer):
    post = EmbeddedPostSerializerVersionOne(many=False)

    class Meta:
        model = EmbeddedPagePost
        fields = ('post',)


class GeneralSerializerVersionOne(DocumentSerializer):
    class Meta:
        model = OutputGeneral
        fields = ('method', 'data', 'platform', 'lang_code', 'ver_api')


class ProfileSerializerVersionOne(DocumentSerializer):
    class Meta:
        model = OutputProfile
        fields = ('username', 'first_name', 'last_name', 'picture', 'number_of_follower', 'number_of_following',
                  'number_of_posts', 'date_of_join')


class CreatePostSerializerVersion1(DocumentSerializer):
    publisher = EmbeddedUserSerializerVersionOne(many=False)
    post = EmbeddedPostSerializerVersionOne(many=False)

    class Meta:
        model = OutputCreatePost
        fields = ('publisher', 'post')


class PagePostSerializerVersionOne(DocumentSerializer):
    posts = EmbeddedPagePostSerializerVersionOne(many=True)

    class Meta:
        model = OutputPagePost
        fields = ('posts', )


class HomePageSerializerVersionOne(DocumentSerializer):
    posts = CreatePostSerializerVersion1(many=True)

    class Meta:
        model = OutputHomePage
        fields = ('posts', )


class ProfileFollowSerializerVersionOne(EmbeddedDocumentSerializer):
    class Meta:
        model = OutputProfile
        fields = ('username', 'first_name', 'last_name', 'picture')


class CommentSerializerVersionOne(DocumentSerializer):
    comments = EmbeddedCommentsSerializerVersionOne(many=True)

    class Meta:
        model = OutputComment
        fields = ('comments', )


class LikeSerializerVersionOne(DocumentSerializer):
    likes = EmbeddedLikeSerializerVersionOne(many=True)

    class Meta:
        model = OutputLike
        fields = ('likes', )


class GetFollowersSerializerVersionOne(DocumentSerializer):
    followers = ProfileFollowSerializerVersionOne(many=True)

    class Meta:
        model = OutputFollowers
        fields = ('followers', )


class GetFollowingsSerializerVersionOne(DocumentSerializer):
    followings = ProfileFollowSerializerVersionOne(many=True)

    class Meta:
        model = OutputFollowings
        fields = ('followings',)
