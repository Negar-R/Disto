import os
import logging

from bson import ObjectId
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from LikeInstaProject import mongo_client_obj
from instagram.models import Profile

logger = logging.getLogger(__name__)


@csrf_exempt
def upload_picture(request):
    try:
        if request.method == 'POST':
            image = request.FILES.get('image')
            profile_id = request.POST.get('profile_id')
            image_basename = os.path.basename(image.name)
            open('images/' + image_basename, 'wb').write(image.file.read())
            image_location = 'images/' + image_basename
            path = os.path.join(settings.BASE_DIR, image_location)

            mongo_client_obj.update_data(Profile,
                                         {'_id': ObjectId(profile_id)},
                                         {"$set": {'picture': path}},
                                         upsert=False)

            return HttpResponse(path, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("upload_picture : " + str(e))
        raise Exception(str(e))
