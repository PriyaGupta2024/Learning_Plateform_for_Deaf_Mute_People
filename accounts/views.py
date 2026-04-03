from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
import logging

logger = logging.getLogger(__name__)

# Try to import learning models at module level, but handle gracefully if app not ready.
try:
    from learning.models import UserProgress, SignTest, Video
    LEARNING_AVAILABLE = True
except Exception as e:
    # learning app not installed or import error; keep flags so function can still run
    logger.debug("learning.models not available at import time: %s", e)
    UserProgress = None
    SignTest = None
    Video = None
    LEARNING_AVAILABLE = False


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            logger.info("Signup invalid: %s", form.errors.as_json())
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def dashboard(request):
    """
    User dashboard / profile.
    Shows recent progress, recent sign tests, quick actions.
    """
    user = request.user

    # Default safe values
    videos_progress = []
    sign_tests = []
    recent_videos = []
    completed_count = 0
    total_lessons = 0
    avg_progress = 0
    recent_progress = []

    if LEARNING_AVAILABLE and UserProgress is not None and Video is not None and SignTest is not None:
        try:
            # Recent progress entries for this user (latest 6)
            videos_progress = (
                UserProgress.objects.filter(user=user)
                .select_related('video')
                .order_by('-last_watched')[:6]
            )

            # Recent sign tests for user
            sign_tests = SignTest.objects.filter(user=user).order_by('-timestamp')[:6]

            # Suggest recent videos (if user has no progress)
            recent_videos = Video.objects.all().order_by('-id')[:6]

            # Stats
            prog_qs = UserProgress.objects.filter(user=user)
            total_lessons = Video.objects.count()
            completed_count = prog_qs.filter(completed=True).count()

            # Use Avg correctly (returns None if no rows)
            avg_val = prog_qs.aggregate(avg=Avg('progress'))['avg'] or 0
            # If avg stored as fraction (0..1) and you want percent multiply by 100 here.
            avg_progress = avg_val

            recent_progress = prog_qs.order_by('-last_watched')[:6]

        except Exception as e:
            # If any runtime error occurs while querying, log and leave defaults
            logger.debug("Error while querying learning models in dashboard: %s", e)

    # Build context
    context = {
        'user': user,
        'videos_progress': videos_progress,
        'sign_tests': sign_tests,
        'recent_videos': recent_videos,
        'completed_count': completed_count,
        'total_lessons': total_lessons,
        'avg_progress': avg_progress,
        'recent_progress': recent_progress,
    }

    return render(request, 'dashboard.html', context)
