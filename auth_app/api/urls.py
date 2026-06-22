"""URL routes for the auth_app API (registration, login, email check)."""
from django.urls import path

from .views import EmailCheckView, LoginView, RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
