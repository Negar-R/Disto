from rest_framework_mongoengine.serializers import DocumentSerializer
from posts.models import Post


class PostSerializer(DocumentSerializer):
    class Meta:
        model = Post
        fields = '__all__'
