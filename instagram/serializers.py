from rest_framework_mongoengine.serializers import DocumentSerializer
from instagram.models import Profile, FollowingRelation, Post


# PROFILE SERIALIZERS
class ProfileSerializer(DocumentSerializer):
    class Meta:
        model = Profile
        fields = ('username', 'last_name', 'first_name', 'picture')


class FollowingRelationSerializer(DocumentSerializer):
    class Meta:
        model = FollowingRelation
        fields = ('follower', )


# POST SERIALIZERS
class PostSerializer(DocumentSerializer):
    class Meta:
        model = Post
        exclude = ('likes', 'comments', 'published_date')