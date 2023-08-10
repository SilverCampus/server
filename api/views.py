from campus.models import *
from campus.serializers import (UserSerializer, SearchCoursesSerializer, CourseVideoListSerializer, PurchasedCoursesSerializer)

from rest_framework.generics import ListAPIView

from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

# 검색어 입력하면 해당 검색어가 포함된 Course 모델의 인스턴스 반환하는 API
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def search_courses(request):
    keyword = request.GET.get('keyword') # URL의 쿼리 매개변수에서 'keyword'를 가져옴
    if keyword is None:
        return Response({"message": "Keyword is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Course 릴레이션에서 keyword를 포함한 강좌들 가져오기!
    courses = Course.objects.filter(title__icontains=keyword)

    if not courses.exists(): # 검색 결과가 없을 때 반환할 메세지
        return Response({"message": "검색 결과가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 찾은 객체들을 시리얼라이즈
    serializer = SearchCoursesSerializer(courses, many=True) # 이 부분 프론트엔드 파트가 요구하는 대로 나중에 수정 ㄱ
    return Response(serializer.data, status=status.HTTP_200_OK)


# Course와 연결된 Video list 반환하는 뷰 (GET)
class CourseVideoListView(ListAPIView):
    serializer_class = CourseVideoListSerializer

    # list 수정하지 않아도, get_queryset() 함수만 오버라이딩 해도 충분!
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Video.objects.filter(course__id = course_id)
    

# 로그인한 사용자가 특정 강의 구매하기
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,)) #로그인한 사용자만 접근 가능
def purchased(request):
    pass

# 로그인한 사용자가 구매한 강의 목록들 반환하는 API
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) #로그인한 사용자만 접근 가능
def purchased_courses(request):
    user = request.user # 로그인한 사용자 객체 얻기
    enrolls = Enroll.objects.filter(user=user)

    courses = [enroll.course for enroll in enrolls]
    serializer = PurchasedCoursesSerializer(courses, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)