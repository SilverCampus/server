from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegisterView, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'category', CategoryViewSet)
# router.register(r'instructor', InstructorViewSet)
router.register(r'course', CourseViewSet)
router.register(r'video', VideoViewSet)
router.register(r'like', LikeViewSet)
router.register(r'enroll', EnrollViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'question', QuestionViewSet)
router.register(r'recentlywatched',RecentlyWatchedViewSet)
router.register(r'boardpostlikes', BoardPostLikeViewSet)
router.register(r'boardposts', BoardPostViewSet)
router.register(r'boardpostcomments', BoardPostCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='user-register'),            # Api 문서 Ok
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Api 문서 Ok
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),       # Api 문서 Ok
]

