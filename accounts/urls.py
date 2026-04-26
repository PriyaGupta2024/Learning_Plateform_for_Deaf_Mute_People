from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import EmailOrUsernameAuthenticationForm

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.CustomLoginView.as_view(
        template_name='login.html',
        authentication_form=EmailOrUsernameAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
