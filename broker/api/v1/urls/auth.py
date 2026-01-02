# broker/api/v1/urls/auth.py
from django.urls import path
from ..views.auth import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    ChangePasswordView,
    LogoutView
)

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]