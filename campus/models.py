from django.db import models
from django.contrib.auth.models import  AbstractUser

# 커스티마이징 한 User
class User(AbstractUser):
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True) # 생일
    nickname = models.CharField(max_length=30, null=True, blank=True) # 사용자의 닉네임
    is_instructor = models.BooleanField(default=True)  # 슈퍼 유저 만들 때 자동으로 is_instructor True
    

# 카테고리
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# 강좌 릴레이션
class Course(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    instructor = models.ForeignKey(User, related_name='course', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='course' , on_delete=models.CASCADE)
    thumbnail = models.CharField(max_length=500, blank=True, null=True) # 나중에 s3 경로 넣어줄 것
    is_live = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# 비디오 릴레이션
class Video(models.Model):
    title = models.CharField(max_length=500)
    video_file = models.CharField(max_length=500)  # 실제 영상 파일을 저장할 필드 s3에!!!
    course = models.ForeignKey(Course, related_name='video', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

# 좋아요 릴레이션
class Like(models.Model):
    course = models.ForeignKey(Course, related_name='like', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='like', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}의 {self.course}에 대한 좋아요" 

# 등록 릴레이션
class Enroll(models.Model):
    course = models.ForeignKey(Course, related_name='enroll', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='enroll', on_delete=models.CASCADE)
    transaction_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return  f"{self.user}의 {self.course}에 대한 수업 등록"


# 질문 릴레이션
class Question(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    student = models.ForeignKey(User, related_name='question', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

# 답변 릴레이션
class Comment(models.Model):
    content = models.TextField()
    instructor = models.ForeignKey(User, related_name='comment', on_delete=models.CASCADE) 
    question = models.ForeignKey(Question, related_name='comment', on_delete=models.CASCADE)    

    def __str__(self):
        return self.content