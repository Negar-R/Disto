import os
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from LikeInstaProject import mongo_client_obj
from instagram.models import UploadedImage

logger = logging.getLogger(__name__)


@csrf_exempt
def upload_picture(request):
    try:
        if request.method == 'POST':
            image = request.FILES.get('image')
            if image:
                image_basename = os.path.basename(image.name)
                open('images\\' + image_basename, 'wb').write(image.file.read())
                image_location = 'images\\' + image_basename
                path = os.path.join(settings.BASE_DIR, image_location)

                image_obj = mongo_client_obj.insert_one_data(UploadedImage, {'image_address': path})

                return JsonResponse({'_id': str(image_obj._id),
                                     'address': image_obj.image_address},
                                    status=status.HTTP_200_OK)
            else:
                return JsonResponse({'_id': None,
                                     'address': None},
                                    status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("upload_picture : " + str(e))
        raise Exception(str(e))
