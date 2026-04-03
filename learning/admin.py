from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin.sites import NotRegistered
from .models import Video, Quiz, UserResponse, UserProgress,Question
from .models import QuizAttempt


# -------------------------
# VIDEO ADMIN
# -------------------------
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_at', 'preview_video')
    search_fields = ('title',)
    readonly_fields = ('uploaded_at',)

    def preview_video(self, obj):
        """Show a small playable video preview in the admin panel"""
        if obj.video_file:
            return format_html(
                '<video width="200" controls>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support video.'
                '</video>', obj.video_file.url
            )
        return "No video uploaded"
    preview_video.short_description = "Preview"


# -------------------------
# QUIZ ADMIN
# -------------------------

# avoid AlreadyRegistered crash while developing
try:
    admin.site.unregister(Quiz)
except NotRegistered:
    pass

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    



@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'score', 'total', 'created_at')
    list_filter = ('quiz', 'created_at')
    search_fields = ('user__username', 'quiz__title')
    

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'text', 'correct_option')
    list_filter = ('quiz',)
    search_fields = ('text',)

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'selected_option', 'correct', 'created_at')
    list_filter = ('quiz', 'correct')
    search_fields = ('user__username',)

# -------------------------
# USER PROGRESS ADMIN
# -------------------------
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'progress_display', 'completed', 'last_watched')
    list_filter = ('completed',)
    search_fields = ('user__username', 'video__title')

    def progress_display(self, obj):
        """Display progress as colored percentage bar"""
        color = "#16a34a" if obj.completed else "#2563eb"
        return format_html(
            '<div style="width:150px; background:#eee; border-radius:5px;">'
            '<div style="width:{}%; background:{}; color:white; text-align:center; border-radius:5px;">{}%</div>'
            '</div>',
            obj.progress, color, round(obj.progress, 1)
        )
    progress_display.short_description = "Progress"
    
    
    
