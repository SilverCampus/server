from campus.models import *
from campus.serializers import (UserSerializer, SearchCoursesSerializer, 
                                CourseVideoListSerializer, PurchasedCoursesSerializer, 
                                EnrollSerializer, LikeSerializer, LikedCoursesSerializer,
                                LaunchCourseSerializer, VideoUploadSerializer, AskQuestionSerializer,
                                AnswerQuestionSerializer, CourseDescriptionUpdateSerializer,
                                GetCourseVideoSerializer, LikedCoursesSerializer,
                                GetRecentlyWatchedCoursesSerializer)

from rest_framework.generics import ListAPIView, CreateAPIView

from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from django.core.exceptions import ObjectDoesNotExist

import boto3
from django.conf import settings

# 1번 
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def search_courses(request):
    keyword = request.GET.get('keyword')
    if keyword is None:
        return Response({"message": "Keyword is required"}, status=status.HTTP_400_BAD_REQUEST)

    courses = Course.objects.filter(title__icontains=keyword)
    courses_list = list(courses)

    try:
        category = Category.objects.get(name=keyword)
        related_courses = category.course.all()
        courses_list.extend(related_courses)
    except Category.DoesNotExist:
        # 카테고리가 없을 경우에 대한 처리는 필요에 따라 작성
        pass

    # 중복 제거
    courses_set = set(courses_list)

    if not courses_set:
        return Response({"message": "검색 결과가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 찾은 객체들을 시리얼라이즈
    serializer = SearchCoursesSerializer(list(courses_set), many=True)
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
    user = request.user
    if user.is_instructor: # User가 강사가 아니라면
        return Response({"error": "User is Instructor"}, status=status.HTTP_400_BAD_REQUEST)

    course_id = request.data.get('course_id')  # request.data가 request.POST보다 일반적

    if not course_id:
        return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    
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
        return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
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
def launch_course(request):
    user = request.user
    if not user.is_instructor: # User가 강사가 아니라면
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)

    # 전달받은 데이터 추출
    title = request.data.get('title')
    price = request.data.get('price')
    description = request.data.get('description')
    category_name = request.data.get('category_name')  # 프론트엔드로부터 이름으로 받음. id x
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
    serializer = LaunchCourseSerializer(course)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 8. 선생님이 자신이 개설한 강좌에 새로운 영상 파일을 추가하는 API 
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
    course_id = request.data.get('course_id')

    try: # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "There is no Course"}, status=status.HTTP_400_BAD_REQUEST)

    if course.instructor != user:
        return Response({"error": "Unmatched btw instructor and course"}, status=status.HTTP_400_BAD_REQUEST)

    # order_in_course 값 확보하기 (추가 함!)
    order_in_course = course.video_count() + 1

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
        course=course,
        order_in_course = order_in_course
    )
    video.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = VideoUploadSerializer(video)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    

# 9. 로그인한 학생이 자신이 수강 중인 강좌에 대해 question 등록하는 API

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def ask_question(request):
    user = request.user

    if user.is_instructor: # User가 강사라면 -> 예외처리
        return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)

    # 프론트엔드로부터 넘겨받는 정보: title, content, course(id)
    title = request.data.get('title')
    content = request.data.get('content')
    course_id = request.data.get('course_id')

    try: # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)
    

    try: # 해당 학생이 넘겨받은 수업 듣고 있는지 체크 -> 아니면 예외처리
        enroll_check = Enroll.objects.get(course=course, user=user)
    except Enroll.DoesNotExist:
        return Response({"error": "User did not enroll this course"}, status=status.HTTP_400_BAD_REQUEST)


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


# 10. 로그인한 선생님이 자신이 개설한 강좌에 대한 question에 comment를 달아주는 API

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def answer_question(request):   # 프론트로부터 넘겨 받아야 할 정보: question_id, content(답글 내용)
    user = request.user

    if not user.is_instructor: # User가 강사가 아니라면 -> 예외처리
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)
    
    question_id = request.data.get('question_id')
    content = request.data.get('content')

    # 해당 질문 객체 뽑아 오기
    try:
        question = Question.objects.get(id=question_id)
    except ObjectDoesNotExist:
        return Response({"error": "There is no that question"}, status=status.HTTP_400_BAD_REQUEST)

    course = question.course  # 해당 질문을 참조하여 강좌 객체 가져오기!

    # 해당 강좌가 현재 로그인한 강사의 강좌가 아닐 때 -> 예외처리
    if course.instructor != user: 
        return Response({"error": "This course is not current Instructor's"}, status=status.HTTP_400_BAD_REQUEST)
    
    comment = Comment(
        content = content,
        instructor = user,
        question = question
    )
    comment.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = AnswerQuestionSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    


# 11. 로그인한 선생님이 자신의 강좌의 description을 수정하는 API (정연이가 API 씀)
@api_view(['PATCH'])
@permission_classes((permissions.IsAuthenticated,)) # courde_id를 url로 받음
def update_course_description(request): # 프론트로부터 넘겨 받아야 할 정보: content(description 내용)
    user = request.user
    course_id = request.data.get('course_id')


    if not user.is_instructor: # User가 강사가 아니라면 -> 예외처리
            return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)
    
    # course_id에 대해 course 객체 받아오기
    try:
        course = Course.objects.get(id=course_id, instructor=user)
    except Course.DoesNotExist: 
        return Response({"error": "Course not found or you are not the instructor."}, status=404)

    # 해당 강좌가 현재 로그인한 강사의 강좌가 아닐 때 -> 예외처리
    if course.instructor != user: 
        return Response({"error": "This course is not current Instructor's"}, status=status.HTTP_400_BAD_REQUEST)
    
    description = request.data.get('description')  # 프론트엔드에서 전달한 description 값 추출
    title = course.title
    price = course.price
    category = course.category
    thumbnail = course.thumbnail
    is_live = course.is_live
    
    if description is not None:
        course = Course(
            id = course_id,
            description = description,
            title = title,
            price = price,
            instructor = user,
            category = category,
            thumbnail = thumbnail,
            is_live = is_live
        ) # description 값 업데이트

        course.save()

    serializer = CourseDescriptionUpdateSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 12. 로그인한 수강자가 자신이 구매한 강좌에 대한 강의들을 시청할 수 있도록 특정 강의 영상을 불러오는 API
# (내가 만들었는데 이거 정연이가 추가한 모델 참고해서 12번 수정 해야해)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) 
def get_course_videos(request): # 프론트로부터 받아야할 것들: course_id, video_num
    user = request.user
    course_id = request.GET.get('course_id')
    order_in_course = request.GET.get('order_in_course')

    if user.is_instructor: # User가 강사라면
        return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)

    try: # 수강자가 해당 강의를 듣고 있는지 체크
        enroll = Enroll.objects.get(user=user, course_id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "This Enroll not found."}, status=404)
    
    # 비디오 모델에서 
    try: # 수강자가 해당 강의를 듣고 있는지 체크
        video = Video.objects.get(course_id=course_id, order_in_course=order_in_course)
    except ObjectDoesNotExist:
        return Response({"error": "This video not found."}, status=404)
    
    serializer = GetCourseVideoSerializer(video)
    return Response(serializer.data, status=status.HTTP_200_OK)
    


# 13. 로그인한 수강자가 가장 최근에 수강한 강좌를 불러오는 API (정연이가 API 할거임)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_recently_watched_courses(request):
    user = request.user
    recently_watched = RecentlyWatched.objects.filter(user=user).order_by('-watched_at')

    if user.is_instructor: # User가 강사라면 에러
        return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 가장 최근에 시청한 강좌 id를 first_course_id에 저장
    if recently_watched:
        first_course_id = recently_watched[0].course_id
    else:
        return Response({"message": "No recently watched courses found."}, status=404)
    
    # first_course_id에 해당하는 course를 response
    try:
        course = Course.objects.get(id=first_course_id)
    except Course.DoesNotExist: 
        return Response({"error": "Course not found."}, status=404)
    
    serializer = GetRecentlyWatchedCoursesSerializer(course, many=False) 
    return Response(serializer.data, status=status.HTTP_200_OK)



# # 14번 가장 최근에 찜한 강의 
# @api_view(['GET'])
# @permission_classes((permissions.IsAuthenticated,))
# def get_recently_liked_courses(request):
#     user = request.user

#     if user.is_instructor:
#         return Response({"error": "User is not a student"}, status=status.HTTP_400_BAD_REQUEST)

#     # Like 모델을 기반으로 사용자의 최근 좋아요 강좌를 가져옵니다.
#     recent_likes = Like.objects.filter(user=user).order_by('-liked_date')[:5]
    
#     # 강좌 목록만 추출
#     liked_courses = [like.course for like in recent_likes]

#     serializer = LikedCoursesSerializer(liked_courses, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)




