

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

# learning/models.py
from cloudinary.models import CloudinaryField


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = CloudinaryField('video', resource_type='video', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# Quizzes Table
# models.py (Quiz model)
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='quizzes')

    def question_count(self):
        return self.questions.count()

    def __str__(self):
        return f"{self.title} (for {self.video.title})"

    class Meta:
        verbose_name_plural = "Quizzes"


# admin.py
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question_count')


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(blank=True, null=True)            # optional caption
    question_image = CloudinaryField('image', resource_type='image', blank=True, null=True)  # NEW
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    correct_option = models.PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3')])

# User Quiz Responses Table
# learning/models.py (add)
class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_option = models.IntegerField(choices=[(1,'1'),(2,'2'),(3,'3')])
    correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Q{self.quiz.id} -> {self.selected_option}"



# Video Progress Table
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0)  # store in %
    completed = models.BooleanField(default=False)
    last_watched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.video.title} ({self.progress}%)"
    
    
from django.utils import timezone

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.total})"
    
    
    
    