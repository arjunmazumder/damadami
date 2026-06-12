import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import UserSession
from .utils import generate_access_token, generate_refresh_token

class AuthenticationService:
    @staticmethod
    def login(email, password):
        user = authenticate(email=email, password=password)
        if not user:
            raise ValueError("Invalid email or password")
        
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token()
        
        # Save refresh token in session
        expires_at = timezone.now() + datetime.timedelta(days=30)
        UserSession.objects.create(
            user=user,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        
        return access_token, refresh_token, user

    @staticmethod
    def refresh_token(old_refresh_token):
        if not old_refresh_token:
            raise ValueError("Refresh token is required")
            
        try:
            session = UserSession.objects.get(refresh_token=old_refresh_token)
        except UserSession.DoesNotExist:
            raise ValueError("Invalid refresh token")
            
        if session.expires_at < timezone.now():
            session.delete()
            raise ValueError("Refresh token expired")
            
        user = session.user
        
        # Generate new tokens
        new_access_token = generate_access_token(user)
        new_refresh_token = generate_refresh_token()
        
        # Rotate refresh token
        session.refresh_token = new_refresh_token
        session.expires_at = timezone.now() + datetime.timedelta(days=30)
        session.save()
        
        return new_access_token, new_refresh_token

    @staticmethod
    def logout(refresh_token):
        if refresh_token:
            UserSession.objects.filter(refresh_token=refresh_token).delete()
