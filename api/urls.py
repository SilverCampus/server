from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('search_courses/', search_courses, name='search_courses'),
    path('course/<int:course_id>/video/', CourseVideoListView.as_view(), name="CourseVideoList"),
]