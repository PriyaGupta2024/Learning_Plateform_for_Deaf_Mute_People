#!/usr/bin/env python
"""
Test the dashboard view rendering to ensure no errors occur.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_learn.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from accounts.views import dashboard

print("\n" + "="*80)
print("DASHBOARD VIEW RENDER TEST")
print("="*80)

# Create test users and requests
factory = RequestFactory()
users = User.objects.filter(is_superuser=False)

print("\n[TEST] Dashboard view rendering for sample users...")

for user in users[:3]:  # Test first 3 users
    request = factory.get('/accounts/dashboard/')
    request.user = user
    
    try:
        # Call the dashboard view
        response = dashboard(request)
        
        # Check if view renders without errors
        if response.status_code == 200:
            print(f"✓ User '{user.username}' - Dashboard renders successfully (Status: 200)")
            
            # Check context data
            if hasattr(response, 'context_data'):
                context = response.context_data
                print(f"  - Total lessons: {context.get('total_lessons', 'N/A')}")
                print(f"  - Completed lessons: {context.get('completed_count', 'N/A')}")
                print(f"  - Overall progress: {context.get('avg_progress', 'N/A'):.1f}%")
        else:
            print(f"✗ User '{user.username}' - Dashboard failed (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ User '{user.username}' - Exception: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("DASHBOARD VIEW RENDER TEST COMPLETE ✓")
print("="*80 + "\n")
