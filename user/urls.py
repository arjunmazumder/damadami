from django.urls import path
from .views import LoginView, RefreshView, LogoutView, RegisterView, UserListView, VerifyOTPView, ForgotPasswordView, ResendOTPView, ResetPasswordView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
    path('resend-otp', ResendOTPView.as_view(), name='resend-otp'),
    path('reset-password', ResetPasswordView.as_view(), name='reset-password'),
    path('login', LoginView.as_view(), name='login'),
    path('getRefreshToken', RefreshView.as_view(), name='refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('users', UserListView.as_view(), name='users-list'),
]
