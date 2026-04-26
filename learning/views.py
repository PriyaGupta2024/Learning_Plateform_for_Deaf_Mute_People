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
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone

import logging
import numpy as np
import cv2
import base64
import os
import json
import zipfile
import tempfile
import tensorflow as tf

MODEL_PATH = os.path.join(settings.BASE_DIR, "learning", "sign_model.keras")
logger = logging.getLogger(__name__)
model = None
model_load_error = None

with open(os.path.join(settings.BASE_DIR, "learning", "class_indices.json")) as f:
    class_indices = json.load(f)

# Reverse mapping: index → label
class_names = {v: k for k, v in class_indices.items()}


def build_sign_model():
    inputs = tf.keras.Input(shape=(224, 224, 3), name='input_layer_1')
    base = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights=None,
        input_tensor=inputs,
        alpha=1.0,
        name='functional'
    )
    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D(name='global_average_pooling2d')(x)
    x = tf.keras.layers.Dropout(0.5, name='dropout')(x)
    outputs = tf.keras.layers.Dense(36, activation='softmax', name='dense')(x)
    return tf.keras.Model(inputs, outputs, name='sequential')


def get_model():
    global model, model_load_error
    if model is not None:
        return model

    if model_load_error is not None:
        raise model_load_error

    try:
        model = build_sign_model()
        with zipfile.ZipFile(MODEL_PATH, 'r') as archive:
            weights_bytes = archive.read('model.weights.h5')

        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as tmp:
            tmp.write(weights_bytes)
            tmp_path = tmp.name

        model.load_weights(tmp_path, by_name=True)
        os.remove(tmp_path)
        return model
    except Exception as exc:
        model_load_error = exc
        raise


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
    context = {}
    if request.method == "POST":
        file = request.FILES.get("image")
        if not file:
            context['upload_error'] = "No image file selected"
            logger.warning("Camera test upload attempted without selecting a file")
        else:
            logger.info("Upload image received: %s (%s bytes)", file.name, file.size)
            try:
                file_bytes = np.frombuffer(file.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if img is None:
                    context['upload_error'] = "Invalid image file"
                    logger.error("Uploaded image could not be decoded: %s", file.name)
                else:
                    label, confidence = predict_frame(img)
                    context['upload_prediction'] = label
                    context['upload_confidence'] = round(confidence * 100, 2)
                    logger.info("Upload prediction result: %s (%.2f%%)", label, confidence * 100)
            except Exception as e:
                context['upload_error'] = str(e)
                logger.exception("Error processing uploaded image")
    return render(request, "learning/camera_test.html", context)


# ==============================
# ===== LESSON LIST PAGE =======
# ==============================

def lesson_list(request):
    videos = Video.objects.all().order_by('order')

    overall_progress = 0

    # initialize default values for all videos
    for video in videos:
        video.progress = 0.0
        video.completed = False

    if request.user.is_authenticated:
        # Get individual video progress
        rows = UserProgress.objects.filter(
            user=request.user,
            video__in=videos
        ).values_list('video_id', 'progress', 'completed')
        progress_map = {vid: {'progress': prog, 'completed': comp} for vid, prog, comp in rows}

        for video in videos:
            progress_data = progress_map.get(video.id, {'progress': 0.0, 'completed': False})
            video.progress = progress_data['progress']
            video.completed = progress_data['completed']

        # Calculate overall progress: completed videos / total videos * 100
        total_videos = videos.count()
        completed_videos = sum(1 for video in videos if video.completed)
        if total_videos > 0:
            overall_progress = (completed_videos / total_videos) * 100

    return render(request, 'learning/lesson_list.html', {
        'videos': videos,
        'overall_progress': overall_progress,
    })


# ==============================
# ===== QUIZ LIST PAGE ========
# ==============================

@login_required
def quiz_list(request):
    # Get all quizzes with related video info
    quizzes = Quiz.objects.select_related('video').annotate(
        ordering=Case(
            When(video__title='Learn Alphabets A - H', then=Value(1)),
            When(video__title='Learn Alphabets I - Q', then=Value(2)),
            When(video__title='Learn Alphabets R - Z', then=Value(3)),
            When(video__title='Learn Numbers 1 - 10', then=Value(4)),
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by('ordering')

    # Get user's quiz attempts, ordered newest first
    user_attempts_qs = QuizAttempt.objects.filter(user=request.user).select_related('quiz').order_by('-created_at')
    user_attempts = list(user_attempts_qs)
    attempts_by_quiz = {}

    for attempt in user_attempts:
        attempt.dots = [i < attempt.score for i in range(attempt.total)]
        attempt.score_percentage = (attempt.score / attempt.total * 100) if attempt.total > 0 else 0
        if attempt.quiz_id not in attempts_by_quiz:
            attempts_by_quiz[attempt.quiz_id] = attempt

    attempted_quiz_ids = set(attempts_by_quiz.keys())

    # Annotate quiz objects so the template can render without dict access
    for quiz in quizzes:
        quiz.is_attempted = quiz.id in attempted_quiz_ids
        quiz.latest_attempt = attempts_by_quiz.get(quiz.id)

    # Calculate statistics
    total_quizzes = quizzes.count()
    attempted_quizzes = len(attempted_quiz_ids)
    completed_quizzes = sum(1 for attempt in attempts_by_quiz.values() if attempt.score >= attempt.total * 0.7)  # 70% passing
    progress_percentage = (attempted_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0

    # Calculate accuracy
    total_correct = sum(attempt.score for attempt in user_attempts)
    total_questions = sum(attempt.total for attempt in user_attempts)
    accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

    # Get last attempt
    last_attempt = user_attempts[0] if user_attempts else None

    # Get quiz history (recent attempts)
    quiz_history = user_attempts[:10]

    context = {
        'quizzes': quizzes,
        'attempts_by_quiz': attempts_by_quiz,
        'total_quizzes': total_quizzes,
        'attempted_quizzes': attempted_quizzes,
        'completed_quizzes': completed_quizzes,
        'accuracy': accuracy,
        'progress_percentage': progress_percentage,
        'last_attempt': last_attempt,
        'quiz_history': quiz_history,
    }

    return render(request, 'learning/quiz_list.html', context)


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
            question=q,
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

    responses = UserResponse.objects.filter(user=request.user, quiz=quiz).select_related('question')

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
        completed = data.get("completed", False)

        video = Video.objects.get(id=video_id)

        progress_obj, _ = UserProgress.objects.get_or_create(
            user=request.user,
            video=video
        )

        progress_obj.progress = progress
        if completed:
            progress_obj.completed = True
            progress_obj.progress = 100  # Ensure progress is 100% when completed
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

    current_model = get_model()
    prediction = current_model.predict(cropped, verbose=0)

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
        try:
            file = request.FILES.get("image")
            if not file:
                return JsonResponse({"error": "No image file uploaded"}, status=400)

            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img is None:
                return JsonResponse({"error": "Invalid image file"}, status=400)

            label, confidence = predict_frame(img)

            return JsonResponse({
                "prediction": label,
                "confidence": round(confidence * 100, 2)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)