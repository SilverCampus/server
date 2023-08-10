from django.urls import path, include
from .views import *

urlpatterns = [
    path('search_courses/', search_courses, name='search_courses'),             # 1번
    path('course/<int:course_id>/video/', CourseVideoListView.as_view(), name="CourseVideoList"),  # 2번
    path('course-enroll/', course_enroll, name='course-enroll'),                # 3번
    path('purchased-courses/', purchased_courses, name='purchased-courses'),    # 4번
]