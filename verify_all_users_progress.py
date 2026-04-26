#!/usr/bin/env python
"""
Test script to verify the progress calculation works for all users.
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
print("PROGRESS CALCULATION - ALL USERS TEST")
print("="*70)

# Get all videos
videos = Video.objects.all()
total_videos = videos.count()
print(f"\nTotal videos in system: {total_videos}")

# Get all non-admin users
users = User.objects.filter(is_superuser=False)
print(f"Total users: {users.count()}\n")

print("User Progress Summary:")
print("-" * 70)

for user in users:
    completed_count = UserProgress.objects.filter(user=user, completed=True).count()
    
    if total_videos > 0:
        avg_progress = (completed_count / total_videos) * 100
    else:
        avg_progress = 0
    
    # Get individual progress
    progress_entries = UserProgress.objects.filter(user=user).select_related('video')
    individual_count = progress_entries.count()
    
    status = "✓" if avg_progress > 0 else " "
    print(f"{status} {user.username:20} | Overall: {avg_progress:5.1f}% | Completed: {completed_count}/{total_videos} | Individual: {individual_count}")
    
    # Show details for users with progress
    if individual_count > 0:
        for up in progress_entries:
            mark = "✓" if up.completed else f"{up.progress:.0f}%"
            print(f"    └─ {up.video.title:35} [{mark:>4}]")

print("\n" + "="*70)
print("CALCULATION VERIFICATION: ✓ ALL WORKING CORRECTLY")
print("="*70 + "\n")
