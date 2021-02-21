from LikeInstaProject.mongo_client import mongo_client_obj
from .celery import app as celery_app

__all__ = ['celery_app']