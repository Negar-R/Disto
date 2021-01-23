from rest_framework_mongoengine.routers import DefaultRouter
from django.urls import path
from posts.views import PostView

urlpatterns = [
    path('menu/', PostView.as_view(), name='menu'),
]
