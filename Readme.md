# 🧠 VAANI – Indian Sign Language Learning Platform

VAANI is a web-based Indian Sign Language learning platform built using Django. It helps beginners learn sign language through structured video lessons, interactive quizzes, and real-time gesture detection using a machine learning model.

---

## 🚀 Features

### 📚 Learning System
- Video-based lessons for sign language
- Smooth video streaming using Cloudinary
- Organized learning flow for beginners

### 🧠 Quiz System
- Image-based multiple-choice questions
- Each lesson has related quizzes
- User performance tracking

### 📊 Progress Tracking
- Tracks user learning progress in real-time
- Marks completion based on performance

### 🤖 Sign Detection (ML Integration)
- Real-time gesture detection using webcam
- Built using MobileNetV2
- Supports:
  - Webcam capture
  - Image upload for prediction

---

## 🛠️ Tech Stack

Frontend:
- HTML
- Tailwind CSS
- JavaScript

Backend:
- Django (Python)

Machine Learning:
- TensorFlow / Keras
- MobileNetV2

Storage:
- Cloudinary (for videos)

---

## 📁 Project Structure
# 🧠 VAANI – Indian Sign Language Learning Platform

VAANI is a web-based Indian Sign Language learning platform built using Django. It helps beginners learn sign language through structured video lessons, interactive quizzes, and real-time gesture detection using a machine learning model.

---

## 🚀 Features

### 📚 Learning System
- Video-based lessons for sign language
- Smooth video streaming using Cloudinary
- Organized learning flow for beginners

### 🧠 Quiz System
- Image-based multiple-choice questions
- Each lesson has related quizzes
- User performance tracking

### 📊 Progress Tracking
- Tracks user learning progress in real-time
- Marks completion based on performance

### 🤖 Sign Detection (ML Integration)
- Real-time gesture detection using webcam
- Built using MobileNetV2
- Supports:
  - Webcam capture
  - Image upload for prediction

---

## 🛠️ Tech Stack

Frontend:
- HTML
- Tailwind CSS
- JavaScript

Backend:
- Django (Python)

Machine Learning:
- TensorFlow / Keras
- MobileNetV2

Storage:
- Cloudinary (for videos)

---

## 📁 Project Structure
sign_learn/
│
├── accounts/
├── learning/
│ ├── templates/
│ ├── templatetags/
│ ├── sign_model.keras
│ ├── class_indices.json
│ └── views.py
│
├── sign_learn/
├── templates/
├── static/
├── db.sqlite3
└── manage.py


---

## ⚙️ Installation & Setup

### 1. Clone the Repository

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
git clone https://github.com/PriyaGupta2024/Learning_Plateform_for_Deaf_Mute_People.git

cd vaani-sign-language


### 2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

### 3. Install Dependencies
nstall django tensorflow opencv-python numpy pillow cloudinary

### 4. Setup Database
python manage.py makemigrations
python manage.py migrate

### 5. Create Superuser (Optional)
python manage.py createsuperuser

### 6. Run Server
python manage.py runserver
Open in browser:
Open in browser:
http://127.0.0.1:8000/


---

## 🤖 ML Model Setup

Make sure these files are present inside the `learning/` folder:

- sign_model.keras
- class_indices.json

---

## 📸 How Sign Detection Works

1. Webcam captures image  
2. Hand region (ROI) is extracted  
3. Image is preprocessed (resize, normalize)  
4. Model predicts gesture  
5. Result is displayed  

---

## ⚠️ Challenges Faced

- Incorrect predictions due to training vs real-world mismatch  
- Issues with .h5 vs .keras model formats  
- Django template errors  
- SQLite database locking  
- Cloudinary integration setup  

---

## ✅ Solutions

- Standardized preprocessing  
- Used .keras model format  
- Debugged using logs  
- Improved database handling  
- Restructured quiz models  

---

## 🌟 Future Improvements

- Add MediaPipe for better hand tracking  
- Improve model accuracy  
- Deploy on cloud  
- Add real-time continuous prediction  

---

## 🎥 Demo Video

Watch the working of VAANI (Sign Detection + Learning System):

<video src="demo_video/ISL_Recording_video.mp4" controls width="600"></video>

## 👩‍💻 Author

Priya Gupta  
Final Year Engineering Student (2026)  
Interested in Full Stack Development + AI/ML

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
