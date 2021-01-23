from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from LikeInstaProject.mongoClient import mongo_client_obj
from posts.serializers import PostSerializer
from posts.models import Post
import json

# Create your views here.


class PostView(View):
    def get(self, request):
        print("IM IN GET METHOD")
        try:
            posts = mongo_client_obj.fetch_data('posts')
            # TODO : post is a mongo cursor objects ... return in as an json
            print(posts, " *** ", type(posts))
            return JsonResponse(posts, safe=False)
        except Exception as err:
            print("!!!!! ", err)
            return HttpResponse("There is not any post yet")

    def post(self, request):
        recieved_post = json.loads(request.body)
        print("@@@ This is recieved data : ", recieved_post, " TYPE : ", type(recieved_post))
        new_post = mongo_client_obj.insert_data('posts', **recieved_post)
        return HttpResponse("Your post committed successfully!")

