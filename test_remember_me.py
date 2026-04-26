#!/usr/bin/env python
"""
Test script to verify the "Remember Me" functionality works correctly.
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
from accounts.views import CustomLoginView
from accounts.forms import EmailOrUsernameAuthenticationForm

print("\n" + "="*80)
print("REMEMBER ME FUNCTIONALITY TEST")
print("="*80)

# Create test client
client = Client()

# Get a test user
test_user = User.objects.filter(is_superuser=False).first()
if not test_user:
    print("❌ No test user found. Please create a user first.")
    sys.exit(1)

print(f"\n[1] Testing with user: {test_user.username}")

# Test 1: Login WITHOUT "Remember Me" (should expire on browser close)
print("\n[2] Test 1: Login WITHOUT 'Remember Me' checkbox")
response = client.post('/accounts/login/', {
    'username': test_user.username,
    'password': 'testpassword123',  # This might need to be adjusted
    'remember_me': ''  # Empty/unchecked
})

if response.status_code == 302:  # Redirect after successful login
    print("✓ Login successful (redirect to dashboard)")
    # Check session expiry
    session_expiry = client.session.get_expiry_age()
    if session_expiry == 0:
        print("✓ Session set to expire on browser close (expiry_age = 0)")
    else:
        print(f"❌ Session expiry unexpected: {session_expiry}")
else:
    print(f"❌ Login failed with status: {response.status_code}")
    print("Note: This test assumes password is 'testpassword123'")

# Test 2: Login WITH "Remember Me" (should persist for 2 weeks)
print("\n[3] Test 2: Login WITH 'Remember Me' checkbox")
client.logout()  # Clear session
response = client.post('/accounts/login/', {
    'username': test_user.username,
    'password': 'testpassword123',
    'remember_me': 'on'  # Checked
})

if response.status_code == 302:
    print("✓ Login successful (redirect to dashboard)")
    # Check session expiry
    session_expiry = client.session.get_expiry_age()
    expected_expiry = 1209600  # 2 weeks in seconds
    if session_expiry == expected_expiry:
        print(f"✓ Session set to persist for 2 weeks (expiry_age = {session_expiry})")
    else:
        print(f"❌ Session expiry unexpected: {session_expiry}, expected: {expected_expiry}")
else:
    print(f"❌ Login failed with status: {response.status_code}")

# Test 3: Verify form field exists
print("\n[4] Test 3: Verify form field configuration")
factory = RequestFactory()
request = factory.get('/accounts/login/')
view = CustomLoginView()
view.setup(request)

# Check if the view has the correct template and form
if view.template_name == 'login.html':
    print("✓ Login view uses correct template")
else:
    print(f"❌ Wrong template: {view.template_name}")

print("\n" + "="*80)
print("REMEMBER ME TEST COMPLETE")
print("="*80)
print("\nTo manually test:")
print("1. Open browser and login with 'Remember Me' checked")
print("2. Close browser completely")
print("3. Reopen browser and visit the site - should still be logged in")
print("4. Login without 'Remember Me' checked")
print("5. Close browser - should be logged out")
print("="*80 + "\n")
