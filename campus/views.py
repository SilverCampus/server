from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *
from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# 회원가입
@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def register(request): 
    # if request.method == 'GET':
    #     return Response({"message": "Please provide username, password, etc. to register."}, status=status.HTTP_200_OK)

    # Post
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) # 성공적 -> 201
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # valid하지 않으면 400 Error

# 로그인
@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def login(request): # 로그인
    if request.method == 'GET':
        return Response({"message": "Please provide username and password to login."}, status=status.HTTP_200_OK)
    
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class InstructorViewSet(ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class VideoViewSet(ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class EnrollViewSet(ModelViewSet):
    queryset = Enroll.objects.all()
    serializer_class = EnrollSerializer

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer                   

