from django.urls import path
from .views import LoginView, RefreshView, LogoutView, RegisterView, UserListView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('getRefreshToken', RefreshView.as_view(), name='refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('users', UserListView.as_view(), name='users-list'),
]
