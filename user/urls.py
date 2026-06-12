from django.urls import path
from .views import LoginView, RefreshView, LogoutView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('getRefreshToken', RefreshView.as_view(), name='refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
]
