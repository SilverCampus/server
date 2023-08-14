from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardPostViewSet, BoardCommentViewSet, BoardPostLikeViewSet

router = DefaultRouter()
router.register('posts', BoardPostViewSet)
router.register('comments', BoardCommentViewSet)
router.register('likes', BoardPostLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
