from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import register, login

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'instructor', InstructorViewSet)
router.register(r'course', CourseViewSet)
router.register(r'video', VideoViewSet)
router.register(r'like', LikeViewSet)
router.register(r'enroll', EnrollViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'question', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
]

