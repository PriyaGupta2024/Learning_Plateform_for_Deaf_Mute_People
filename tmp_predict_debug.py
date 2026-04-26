import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_learn.settings')
sys.path.insert(0, os.getcwd())
import django
django.setup()
import numpy as np
from learning.views import predict_frame
arr = np.zeros((224,224,3), dtype='uint8')
try:
    print('result:', predict_frame(arr))
except Exception as e:
    import traceback
    traceback.print_exc()
