from django.urls import path
from instagram.views import ProfileAPIView, PostAPIView, FirstPageAPIView, ReactOnPostAPIView, FollowAPIView

urlpatterns = [
    # PROFILE URLS
    path('profile', ProfileAPIView.as_view(), name='profile'),
    path('follow', FollowAPIView.as_view(), name='follow'),

    # POST URLS
    path('post', PostAPIView.as_view(), name='post'),
    path('page', FirstPageAPIView.as_view(), name='page'),
    path('react', ReactOnPostAPIView.as_view(), name='react'),
]
