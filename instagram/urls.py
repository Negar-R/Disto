from django.urls import path
from instagram.views import ProfileAPIView, FollowAPIView,\
                            PostAPIView, FirstPageAPIView, reactOnPostAPIView

urlpatterns = [
    # PROFILE URLS
    path('profile', ProfileAPIView.as_view(), name='profile'),
    # path('profile/<str:username>', GetProfileAPIViewDetail.as_view(), name='get_profile'),
    path('follow/<str:id>', FollowAPIView.as_view(), name='follow'),

    # POST URLS
    path('post', PostAPIView.as_view(), name='post'),
    path('page/<str:owner_id>', FirstPageAPIView.as_view(), name='page'),
    path('reaction/<str:post_id>', reactOnPostAPIView, name='reaction'),
]
