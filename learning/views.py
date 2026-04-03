# learning/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import (
    Video, Quiz, UserResponse,
    UserProgress, Question, QuizAttempt
)

from django.db import transaction
from django.utils import timezone

import numpy as np
import cv2
import base64
import os
import json

from tensorflow.keras.models import load_model


# ==============================
# ===== LOAD ML MODEL ONCE =====
# ==============================

MODEL_PATH = os.path.join(settings.BASE_DIR, "learning", "sign_model.keras")
model = load_model(MODEL_PATH)

with open(os.path.join(settings.BASE_DIR, "learning", "class_indices.json")) as f:
    class_indices = json.load(f)

# Reverse mapping: index → label
class_names = {v: k for k, v in class_indices.items()}


# ==============================
# ========= HOME PAGE ==========
# ==============================

def home(request):
    videos = Video.objects.all().order_by('-id')[:8]
    return render(request, 'home.html', {'videos': videos})


# ==============================
# ===== CAMERA TEST PAGE =======
# ==============================

@login_required
def camera_test(request):
    return render(request, "learning/camera_test.html", {})


# ==============================
# ===== LESSON LIST PAGE =======
# ==============================

def lesson_list(request):
    videos = Video.objects.all().order_by('-uploaded_at')

    progress_map = {}
    if request.user.is_authenticated:
        rows = UserProgress.objects.filter(
            user=request.user,
            video__in=videos
        ).values_list('video_id', 'progress')
        progress_map = {vid: prog for vid, prog in rows}

    return render(request, 'learning/lesson_list.html', {
        'videos': videos,
        'progress_map': progress_map,
    })


# ==============================
# ===== VIDEO DETAIL PAGE ======
# ==============================

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)

    user_progress = None
    if request.user.is_authenticated:
        user_progress = UserProgress.objects.filter(
            user=request.user,
            video=video
        ).first()

    videos = list(Video.objects.order_by('id'))
    current_index = videos.index(video)

    prev_video = videos[current_index - 1] if current_index > 0 else None
    next_video = videos[current_index + 1] if current_index < len(videos) - 1 else None

    context = {
        'video': video,
        'quizzes': video.quizzes.all() if hasattr(video, 'quizzes') else [],
        'user_progress': user_progress,
        'prev_video': prev_video,
        'next_video': next_video,
    }

    return render(request, 'learning/video_detail.html', context)


# ==============================
# ===== QUIZ SECTION ===========
# ==============================

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(Question.objects.filter(quiz=quiz).order_by('id'))

    return render(request, 'learning/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def submit_quiz(request, quiz_id):

    if request.method != 'POST':
        return redirect('quiz_detail', quiz_id=quiz_id)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user

    UserResponse.objects.filter(user=user, quiz=quiz).delete()

    questions = list(Question.objects.filter(quiz=quiz).order_by('id'))
    total = len(questions)
    correct_count = 0

    for q in questions:
        key = f"question_{q.id}"
        raw = request.POST.get(key, '')

        try:
            selected = int(raw) if raw != '' else None
        except ValueError:
            selected = None

        is_correct = (selected is not None and selected == q.correct_option)

        if is_correct:
            correct_count += 1

        UserResponse.objects.create(
            user=user,
            quiz=quiz,
            selected_option=(selected if selected is not None else 0),
            correct=is_correct
        )

    attempt = QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        score=correct_count,
        total=total
    )

    percent = (correct_count / total) * 100 if total else 0

    video = getattr(quiz, 'video', None)
    if video:
        up, _ = UserProgress.objects.get_or_create(user=user, video=video)
        up.progress = max(up.progress, percent)

        if percent >= 70:
            up.completed = True
            up.progress = max(up.progress, 100)

        up.save()

    messages.success(request, f"You scored {correct_count}/{total} ({percent:.0f}%)")
    return redirect('quiz_result', attempt_id=attempt.id)


@login_required
def quiz_result(request, attempt_id):

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    quiz = attempt.quiz

    responses = list(
        UserResponse.objects.filter(user=request.user, quiz=quiz)
    )

    total = attempt.total
    score = attempt.score
    percent = (score / total) * 100 if total else 0

    return render(request, 'learning/quiz_result.html', {
        'quiz': quiz,
        'responses': responses,
        'score': score,
        'total': total,
        'percent': percent,
        'attempt': attempt,
    })


# ==============================
# ===== PROGRESS UPDATE =========
# ==============================

@csrf_exempt
def update_progress(request, video_id):

    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        progress = float(data.get("progress", 0))

        video = Video.objects.get(id=video_id)

        progress_obj, _ = UserProgress.objects.get_or_create(
            user=request.user,
            video=video
        )

        progress_obj.progress = progress
        progress_obj.completed = progress >= 90
        progress_obj.save()

        return JsonResponse({"status": "ok", "progress": progress_obj.progress})

    return JsonResponse({"status": "unauthorized"}, status=401)


# ==============================
# ===== ML PREDICTION ==========
# ==============================

def predict_frame(frame):

    h, w, _ = frame.shape

    # Crop center 60%
    cropped = frame[int(h * 0.2):int(h * 0.8),
                    int(w * 0.2):int(w * 0.8)]

    cropped = cv2.resize(cropped, (224, 224))
    cropped = cropped.astype("float32") / 255.0
    cropped = np.expand_dims(cropped, axis=0)

    prediction = model.predict(cropped, verbose=0)

    class_index = np.argmax(prediction)
    confidence = float(np.max(prediction))

    if confidence < 0.6:
        return "Adjust Hand Position", confidence

    return class_names[class_index], confidence


@csrf_exempt
def predict_sign(request):

    if request.method == "POST":
        try:
            image_data = request.POST.get("image")

            if not image_data:
                return JsonResponse({"error": "No image received"}, status=400)

            format, imgstr = image_data.split(';base64,')
            image_bytes = base64.b64decode(imgstr)

            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"error": "Invalid image"}, status=400)

            label, confidence = predict_frame(frame)

            return JsonResponse({
                "prediction": label,
                "confidence": round(confidence * 100, 2)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def predict_upload(request):

    if request.method == "POST":

        file = request.FILES.get("image")

        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        label, confidence = predict_frame(img)

        return JsonResponse({
            "prediction": label,
            "confidence": round(confidence*100,2)
        })