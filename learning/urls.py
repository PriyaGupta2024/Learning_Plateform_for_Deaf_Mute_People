# learning/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lesson_list, name='lesson_list'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:response_id>/', views.quiz_result, name='quiz_result'),
    path('camera/', views.camera_test, name='camera_test'),
    path('update-progress/<int:video_id>/', views.update_progress, name='update_progress'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),         # shows quiz & questions
    path('submit-quiz/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),  # POST handler
    path('quiz-result/<int:attempt_id>/', views.quiz_result, name='quiz_result'), # shows result
    path('predict/', views.predict_sign, name='predict_sign'),
    path("predict_upload/", views.predict_upload, name="predict_upload"),





]
