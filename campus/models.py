from django.db import models
from django.contrib.auth.models import  AbstractUser

# 커스티마이징 한 User
class User(AbstractUser):
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=30, null=True, blank=True)
    

# 카테고리
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
# 강사 릴레이션   
class Instructor(models.Model):
    name = models.CharField(max_length=50)
    profile = models.TextField()
    photo = models.ImageField(upload_to='instructor_photos/', null=True, blank=True)

    def __str__(self):
        return self.name


# 강좌 릴레이션
class Course(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    instructor = models.ForeignKey(Instructor, related_name='course', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='course' , on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# 비디오 릴레이션
class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')  # 실제 영상 파일을 저장할 필드
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

    def __str__(self):
        return self.title
    

# 답변 릴레이션
class Comment(models.Model):
    content = models.TextField()
    instructor = models.ForeignKey(Instructor, related_name='comment', on_delete=models.CASCADE) 
    question = models.ForeignKey(Question, related_name='comment', on_delete=models.CASCADE)    

    def __str__(self):
        return self.content