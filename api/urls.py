from django.urls import path, include
from .views import *
from .views import register, login, search_courses

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('search_courses/', search_courses, name='search_courses'),
]