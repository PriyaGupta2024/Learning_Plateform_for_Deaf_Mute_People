from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Case, When, Value, IntegerField
import logging

logger = logging.getLogger(__name__)

# Try to import learning models at module level, but handle gracefully if app not ready.
try:
    from learning.models import UserProgress, Video
    LEARNING_AVAILABLE = True
except Exception as e:
    # learning app not installed or import error; keep flags so function can still run
    logger.debug("learning.models not available at import time: %s", e)
    UserProgress = None
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


class CustomLoginView(LoginView):
    """
    Custom login view that handles "Remember Me" functionality.
    """
    template_name = 'login.html'
    authentication_form = None  # Will be set in __init__ or use default

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        # Call the parent form_valid to perform the actual login
        response = super().form_valid(form)

        # Handle "Remember Me" functionality
        remember_me = self.request.POST.get('remember_me')
        print(f"Remember me: {remember_me}")  # Debug print as requested

        if remember_me:
            # Set session to persist for 2 weeks (1209600 seconds)
            self.request.session.set_expiry(1209600)
            print("Session set to persist for 2 weeks")
        else:
            # Set session to expire on browser close
            self.request.session.set_expiry(0)
            print("Session set to expire on browser close")

        return response


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

    if LEARNING_AVAILABLE and UserProgress is not None and Video is not None:
        try:
            # Recent progress entries for this user (latest 6)
            videos_progress = (
                UserProgress.objects.filter(user=user)
                .select_related('video')
                .order_by('-last_watched')[:6]
            )

            # Suggest recent videos (if user has no progress) - ordered by custom sequence
            recent_videos = Video.objects.all().order_by('order')[:6]

            # Calculate overall progress: completed videos / total videos * 100
            total_lessons = Video.objects.count()
            completed_count = UserProgress.objects.filter(user=user, completed=True).count()
            
            # DEBUG: Log the progress values
            logger.info(f"Dashboard Progress Debug - User ID: {user.id}, Total Lessons: {total_lessons}, Completed Lessons: {completed_count}")
            print(f"[DEBUG] Dashboard Progress - User ID: {user.id}, Total Lessons: {total_lessons}, Completed Lessons: {completed_count}")
            
            if total_lessons > 0:
                avg_progress = (completed_count / total_lessons) * 100
            else:
                avg_progress = 0

            recent_progress = UserProgress.objects.filter(user=user).order_by('-last_watched')[:6]

        except Exception as e:
            # If any runtime error occurs while querying, log and leave defaults
            logger.error("Error while querying learning models in dashboard: %s", e)
            print(f"[ERROR] Dashboard exception: {e}")
            import traceback
            traceback.print_exc()

    # Build context
    context = {
        'user': user,
        'videos_progress': videos_progress,
        'recent_videos': recent_videos,
        'completed_count': completed_count,
        'total_lessons': total_lessons,
        'avg_progress': avg_progress,
        'recent_progress': recent_progress,
    }

    return render(request, 'dashboard.html', context)
