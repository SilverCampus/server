from campus.models import *
from campus.serializers import (UserSerializer, SearchCoursesSerializer, 
                                CourseVideoListSerializer, PurchasedCoursesSerializer, 
                                EnrollSerializer, LikeSerializer, LikedCoursesSerializer,
                                EnrollCourseSerializer, VideoUploadSerializer, AskQuestionSerializer)

from rest_framework.generics import ListAPIView, CreateAPIView

from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from django.core.exceptions import ObjectDoesNotExist

import boto3
from django.conf import settings

# 1. 검색어 입력하면 해당 검색어가 포함된 Course 모델의 인스턴스 반환하는 API
# 추가적으로 카테코리에도 해당되는 거면 다 가져오기!!
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def search_courses(request):
    keyword = request.GET.get('keyword') # URL의 쿼리 매개변수에서 'keyword'를 가져옴
    if keyword is None:
        return Response({"message": "Keyword is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Course 릴레이션에서 keyword를 포함한 강좌들 리스트로 가져오기!
    courses = Course.objects.filter(title__icontains=keyword)

    if not courses.exists(): # 검색 결과가 없을 때 반환할 메세지
        return Response({"message": "검색 결과가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 찾은 객체들을 시리얼라이즈
    serializer = SearchCoursesSerializer(courses, many=True) # 이 부분 프론트엔드 파트가 요구하는 대로 나중에 수정 ㄱ
    return Response(serializer.data, status=status.HTTP_200_OK)


# 2. Course와 연결된 Video list 반환하는 API (GET)
class CourseVideoListView(ListAPIView):
    serializer_class = CourseVideoListSerializer

    # list 수정하지 않아도, get_queryset() 함수만 오버라이딩 해도 충분!
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Video.objects.filter(course__id = course_id)


# 3. 로그인한 사용자가 특정 강좌를 구매하는 API

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def course_enroll(request):
    course_id = request.data.get('course_id')  # request.data가 request.POST보다 일반적
    if not course_id:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    # 사용자가 로그인한 상태이므로 request.user에서 사용자 정보를 가져옵니다.
    user = request.user
    # Enroll 객체를 생성합니다.
    enroll = Enroll(course=course, user=user)
    # DB에 저장합니다.
    enroll.save()
    # 응답을 위한 Serializer를 사용합니다.
    serializer = EnrollSerializer(enroll)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 4. 로그인한 사용자가 구매한 강좌 목록들 반환하는 API

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) #로그인한 사용자만 접근 가능
def purchased_courses(request):
    user = request.user # 로그인한 사용자 객체 얻기
    enrolls = Enroll.objects.filter(user=user)

    courses = [enroll.course for enroll in enrolls]
    serializer = PurchasedCoursesSerializer(courses, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# 5. 로그인한 사용자가 특정 강좌를 찜하는 API

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def course_like(request):
    course_id = request.data.get('course_id')   # request.POST에서 request.data로 수정!
    if not course_id:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    # 사용자가 로그인한 상태이므로 request.user에서 사용자 정보를 가져옵니다.
    user = request.user
    # Enroll 객체를 생성합니다.
    like = Like(course=course, user=user)
    # DB에 저장합니다.
    like.save()
    # 응답을 위한 Serializer를 사용합니다.
    serializer = LikeSerializer(like)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 6. 로그인한 사용자가 찜한 강좌 목록들 반환하는 API

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) # 로그인한 사용자만 접근 가능
def liked_courses(request):
    user = request.user # 로그인한 사용자 객체 얻기
    likes = Like.objects.filter(user=user)

    courses = [like.course for like in likes]
    serializer = LikedCoursesSerializer(courses, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# 7. 로그인한 사용자(강사)가 새로운 강좌를 개설하는 하는 API

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def enroll_course(request):
    user = request.user
    if not user.is_instructor: # User가 강사가 아니라면
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)

    # 선생님일 때 -> 강좌의 데이터 추출
    title = request.data.get('title')
    price = request.data.get('price')
    description = request.data.get('description')
    category_name = request.data.get('category')  # 프론트엔드로부터 이름으로 받음. id x
    # thumbnail = request.data.get('thumbnail')   
    thumbnail = request.FILES.get('thumbnail') # 나중에 S3에 저장하는 로직대로 처리해야!!
    is_live = request.data.get('is_live')
    
    # 카테고리 객체 찾기 (예외 처리를 위해 get_object_or_404를 사용할 수도 있음)
    try:
        category = Category.objects.get(name=category_name)
    except ObjectDoesNotExist:
        return Response({"error": "Category does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    

    # S3 연결
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    # 파일 경로 지정
    file_path = 'images/' + str(thumbnail)

    # S3에 업로드
    s3_client.upload_fileobj(thumbnail, settings.AWS_STORAGE_BUCKET_NAME, file_path, ExtraArgs={'ContentType': 'image/jpeg'})


    # S3 URL 생성
    thumbnail_url = f'{file_path}'


    course = Course(
        title=title,
        price=price,
        description=description,
        instructor=user,  # 강좌의 강사는 현재 로그인해 있는 User
        category=category,
        thumbnail=thumbnail_url,
        is_live=is_live
    )
    course.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = EnrollCourseSerializer(course)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 8. 선생님이 자신이 개설한 강좌에 새로운 영상 파일을 추가하는 API (S3 부분 처리해야!!)
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def video_upload(request):
    user = request.user

    if not user.is_instructor: # User가 강사가 아니라면
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 프론트엔드로부터 넘겨받는 정보: title, video_file, course(id)
    title = request.data.get('title')
    video_file = request.FILES.get('video_file')  # 여길 나중에 FILES로 바꿔야!!
    # video_file = request.data.get('video_file')
    course_id = request.data.get('course')

    try: # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)

    if course.instructor != user:
        return Response({"error": "Unmatched btw instructor and course"}, status=status.HTTP_400_BAD_REQUEST)

    # S3 연결
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    # 파일 경로 지정
    file_path = 'videos/' + str(video_file)

    # S3에 업로드
    s3_client.upload_fileobj(video_file, settings.AWS_STORAGE_BUCKET_NAME, file_path, ExtraArgs={'ContentType': 'video/mp4'})


    # S3 URL 생성
    video_url = f'{file_path}'

    video = Video(
        title=title,
        video_file=video_url,
        course=course
    )
    video.save()


    # Serializer를 사용해 JSON 응답 생성
    serializer = VideoUploadSerializer(video)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    


# 9. 로그인한 학생이 자신이 수강 중은 강좌에 대해 question 등록하는 API

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def ask_question(request):
    user = request.user

    if user.is_instructor: # User가 강사라면 -> 예외처리
        return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)

    # 프론트엔드로부터 넘겨받는 정보: title, content, course(id)
    title = request.data.get('title')
    content = request.data.get('content')
    course_id = request.data.get('course')

    try: # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)
    

    try: # 해당 학생이 넘겨받은 수업 듣고 있는지 체크 -> 아니면 예외처리
        enroll_check = Enroll.objects.get(course=course, user=user)
    except Enroll.DoesNotExist:
        return Response({"error": "User is not enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)


    question = Question(
        title = title,
        content = content,
        student = user,
        course = course
    )
    question.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = AskQuestionSerializer(question)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




# 10. 선생님이 자신이 개설한 강좌에 대한 question에 comment를 다는 API




# 11. 로그인한 선생님이 자신의 강좌의 description을 수정하는 API