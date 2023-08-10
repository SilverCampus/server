from campus.models import *
from campus.serializers import UserSerializer, CourseSerializer, CourseVideoListSerializer

from rest_framework.generics import ListAPIView

from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

# 회원가입 (GET 필요 없어서 지우고 POST만 남겨 놓음)
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def register(request): 
    # Post
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) # 성공적 -> 201
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # valid하지 않으면 400 Error

# 로그인 (GET 필요 없어서 지우고 POST만 남겨 놓음)
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    
    username = request.data.get('username')
    password = request.data.get('password')

    # 입력 검증: username과 password가 None인 경우 처리 (안정성 위해 추가)
    if username is None or password is None:
        return Response({"message": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    # return Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response({"message": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


# 검색어 입력하면 해당 검색어가 포함된 Course 모델의 인스턴스 반환
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
    serializer = CourseSerializer(courses, many=True) # 이 부분 프론트엔드 파트가 요구하는 대로 나중에 수정 ㄱ
    return Response(serializer.data, status=status.HTTP_200_OK)


# Course와 연결된 Video list 반환하는 뷰 (GET)
class CourseVideoListView(ListAPIView):
    serializer_class = CourseVideoListSerializer

    # list 수정하지 않아도, get_queryset() 함수만 오버라이딩 해도 충분!
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Video.objects.filter(course__id = course_id)