from django.urls import path, include
from .views import *

urlpatterns = [
    path('search-courses/', search_courses, name='search-courses'),            # 1번
    path('course/<int:course_id>/video/', CourseVideoListView.as_view(), name="CourseVideoList"),  # 2번
    path('course-enroll/', course_enroll, name='course-enroll'),               # 3번
    path('purchased-courses/', purchased_courses, name='purchased-courses'),   # 4번
    path('course-like/', course_like, name='course-like'),                     # 5번
    path('liked-courses/', liked_courses, name='liked-courses'),               # 6번
    path('enroll-course/', enroll_course, name="enroll-course"),               # 7번
    path('video-upload/', video_upload, name='video-upload'),                   # 8번
]