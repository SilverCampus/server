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
    thumbnail = models.FileField(upload_to='images/') 
    is_live = models.BooleanField(default=False)

    def video_count(self):  # 해당 강좌에 연결된 Video들이 몇 개인지 계산해서 반환해주는 함수
        return self.video.count() # related_name 'video'를 사용함. 따라서 역참조 할 때 video 이용!

    def __str__(self):
        return self.title


# 비디오 릴레이션
class Video(models.Model):
    title = models.CharField(max_length=500)
    video_file = models.FileField(upload_to='videos/')  # 실제 영상 파일을 저장할 필드 s3에!!!
    course = models.ForeignKey(Course, related_name='video', on_delete=models.CASCADE)
    order_in_course = models.IntegerField()  # 연결된 강좌 내에서 몇 번째 강의인지 알려주는 속성 

    def __str__(self):
        return self.title

# 좋아요 릴레이션
class Like(models.Model):
    course = models.ForeignKey(Course, related_name='like', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='like', on_delete=models.CASCADE)
    # liked_date = models.DateTimeField(auto_now_add=True) # 새로 추가

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
    course = models.ForeignKey(Course, related_name='question', on_delete=models.CASCADE)


    def __str__(self):
        return self.title
    

# 답변 릴레이션
class Comment(models.Model):
    content = models.TextField()
    instructor = models.ForeignKey(User, related_name='comment', on_delete=models.CASCADE) 
    question = models.ForeignKey(Question, related_name='comment', on_delete=models.CASCADE)    

    def __str__(self):
        return self.content
    

# 최근 시청 강좌 저장 릴레이션
class RecentlyWatched(models.Model):
    user = models.ForeignKey(User, related_name='recently_watched', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='recently_watched', on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}이 <{self.course.title}>를 ({self.watched_at})에 시청"
    
# 강의 수강 완료 저장 릴레이션    
class VideoCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now=True)