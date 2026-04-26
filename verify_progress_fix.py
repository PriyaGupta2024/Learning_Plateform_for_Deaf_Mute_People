#!/usr/bin/env python
"""
Test script to verify the progress calculation fix.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_learn.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from learning.models import Video, UserProgress
from django.contrib.auth.models import User

print("\n" + "="*70)
print("PROGRESS CALCULATION FIX VERIFICATION")
print("="*70)

# Check if videos exist
videos = Video.objects.all()
print(f"\n[1] Total videos in database: {videos.count()}")
if videos.count() > 0:
    for v in videos[:5]:
        print(f"    - ID {v.id}: {v.title}")
else:
    print("    WARNING: No videos found in database!")

# Check if users exist
users = User.objects.filter(is_superuser=False)
print(f"\n[2] Total non-admin users: {users.count()}")

# Check UserProgress entries
total_progress = UserProgress.objects.count()
print(f"\n[3] Total UserProgress entries: {total_progress}")

if users.count() > 0 and total_progress > 0:
    test_user = users.first()
    print(f"\n[4] Testing progress calculation for user: {test_user.username}")
    
    # Calculate progress the way the dashboard does
    total_lessons = Video.objects.count()
    completed_count = UserProgress.objects.filter(user=test_user, completed=True).count()
    
    print(f"    - Total lessons (all videos): {total_lessons}")
    print(f"    - Completed lessons: {completed_count}")
    
    if total_lessons > 0:
        avg_progress = (completed_count / total_lessons) * 100
    else:
        avg_progress = 0
    
    print(f"    - Overall progress: {avg_progress:.1f}%")
    
    # Show user's individual progress
    user_progress_entries = UserProgress.objects.filter(user=test_user).select_related('video')
    print(f"\n[5] Individual lesson progress for {test_user.username}:")
    if user_progress_entries.count() > 0:
        for up in user_progress_entries[:5]:
            status = "✓ Completed" if up.completed else f"{up.progress:.0f}%"
            print(f"    - {up.video.title}: {status}")
    else:
        print("    - No progress entries yet")
else:
    print("\n[4-5] Skipping progress calculation test (no users or no progress data)")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70 + "\n")
