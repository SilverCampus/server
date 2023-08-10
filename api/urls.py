from django.urls import path, include
from .views import *

urlpatterns = [
    path('search_courses/', search_courses, name='search_courses'),
    path('course/<int:course_id>/video/', CourseVideoListView.as_view(), name="CourseVideoList"),
    path('purchased-courses/', purchased_courses, name='purchased-courses'),
    path('course-enroll/', course_enroll, name='course-enroll'),
]