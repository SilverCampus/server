from rest_framework import serializers
from django.contrib.auth import get_user_model
from campus.models import Course, Category, Instructor, Video, Like, Enroll, Comment, Question, User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'address', 'phone', 'birth_date', 'nickname')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            address=validated_data.get('address', ''),
            phone=validated_data.get('phone', ''),
            birth_date=validated_data.get('birth_date'),
            nickname=validated_data.get('nickname', '')
        )
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'



#######  api 앱에서 쓰는 view 만들 때 쓰는 별도 시리얼라이즈들 ########

# class UserRegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'

class SearchCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CourseVideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'  

class PurchasedCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'       