from campus.serializers import UserSerializer
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

