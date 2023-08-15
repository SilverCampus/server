from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register('posts', BoardPostViewSet)
router.register('comments', BoardCommentViewSet)
router.register('likes', BoardPostLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-post-details/', get_post_details, name='get-post-details'),
]
