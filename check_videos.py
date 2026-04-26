import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_learn.settings')
django.setup()

from learning.models import Video

print("\n=== FIXING VIDEO ORDER ===")
Video.objects.filter(title='Learn Albhabets A - H').update(order=1)
Video.objects.filter(title='Learn Alphabets I - Q').update(order=2)
Video.objects.filter(title='Learn Albhabets R - Z').update(order=3)
Video.objects.filter(title='1 to 10 Tutorial').update(order=4)

print("\n=== UPDATED VIDEO TITLES AND ORDER ===")
for v in Video.objects.all().order_by('order'):
    print(f'Order: {v.order} | Title: "{v.title}"')
