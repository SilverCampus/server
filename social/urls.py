from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

router = DefaultRouter()
router.register('posts', BoardPostViewSet)
router.register('comments', BoardCommentViewSet)
router.register('likes', BoardPostLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-post-details/', get_post_details, name='get-post-details'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('add_like/', views.add_like, name='add_like'),
    path('post_upload/', post_upload, name='post_upload'),
    path('posts/tag/<str:hashtag_name>/', PostsByHashtag.as_view(), name='posts-by-hashtag'),
    
]

