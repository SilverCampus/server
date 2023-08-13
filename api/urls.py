from django.urls import path, include
from .views import *

urlpatterns = [
    path('search-courses/', search_courses, name='search-courses'),            # 1번, api 문서 Ok
    path('course/<int:course_id>/video/', CourseVideoListView.as_view(), name="CourseVideoList"),  # 2번, api 문서 Ok
    path('course-enroll/', course_enroll, name='course-enroll'),               # 3번, api 문서 Ok
    path('purchased-courses/', purchased_courses, name='purchased-courses'),   # 4번, api 문서 Ok
    path('course-like/', course_like, name='course-like'),                     # 5번, api 문서 Ok
    path('liked-courses/', liked_courses, name='liked-courses'),               # 6번, api 문서 Ok
    path('launch-course/', launch_course, name="launch-course"),               # 7번, api 문서 Ok
    path('video-upload/', video_upload, name='video-upload'),                  # 8번, api 문서 Ok
    path('ask-question/', ask_question, name='ask-question'),                  # 9번, api 문서 Ok
    path('answer-question/', answer_question, name='answer-question'),         # 10번,
    path('update-course-description/', update_course_description, name='update-course-description'), # 11번,
    path('get-course-videos/', get_course_videos, name='get-course-videos'),    # 12번,
    path('get-recently-watched-courses/', get_recently_watched_courses, name='get-recently-watched-courses'), #13번, 
    # path('recently-liked-courses/', get_recently_liked_courses, name='recently-liked-courses'), # 14번,
]