import datetime
import random
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from .models import UserSession, UserOTP
from .utils import generate_access_token, generate_refresh_token

class AuthenticationService:
    @staticmethod
    def register(email, password, **kwargs):
        from .models import User
        if User.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists")
            
        user = User.objects.create_user(email=email, password=password, is_active=False, **kwargs)
        
        # Generate and save OTP
        otp_code = f"{random.randint(100000, 999999)}"
        UserOTP.objects.create(user=user, otp=otp_code)
        
        # Send Email
        try:
            send_mail(
                subject='Verify your Damadami account',
                message=f'Your OTP code is {otp_code}',
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # If email fails, we might want to delete the user or handle it
            pass
            
        return user

    @staticmethod
    def login(email, password):
        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Invalid email or password")
            
        if not user.check_password(password):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("User account is not verified. Please check your email for OTP.")
        
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
        
        if not user.is_active:
            raise ValueError("User account is not verified")
        
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

    @staticmethod
    def verify_otp(email, otp):
        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User not found")
            
        if user.is_active:
            raise ValueError("User is already verified")
            
        try:
            user_otp = UserOTP.objects.get(user=user)
        except UserOTP.DoesNotExist:
            raise ValueError("No OTP found for this user")
            
        if user_otp.otp != otp:
            raise ValueError("Invalid OTP")
            
        user.is_active = True
        user.save()
        user_otp.delete()
        return user

    @staticmethod
    def send_otp(email, subject, message_template):
        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User not found")
            
        otp_code = f"{random.randint(100000, 999999)}"
        
        # Delete old OTP if exists
        UserOTP.objects.filter(user=user).delete()
        
        # Create new OTP
        UserOTP.objects.create(user=user, otp=otp_code)
        
        # Send Email
        try:
            send_mail(
                subject=subject,
                message=message_template.format(otp_code=otp_code),
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            pass

    @staticmethod
    def forgot_password(email):
        AuthenticationService.send_otp(
            email=email,
            subject='Damadami - Password Reset',
            message_template='Your OTP code for password reset is {otp_code}'
        )

    @staticmethod
    def resend_otp(email):
        AuthenticationService.send_otp(
            email=email,
            subject='Damadami - Your New OTP',
            message_template='Your new OTP code is {otp_code}'
        )

    @staticmethod
    def reset_password(email, otp, new_password):
        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User not found")
            
        try:
            user_otp = UserOTP.objects.get(user=user)
        except UserOTP.DoesNotExist:
            raise ValueError("No OTP found for this user")
            
        if user_otp.otp != otp:
            raise ValueError("Invalid OTP")
            
        user.set_password(new_password)
        user.is_active = True  # Also activate the user if they were inactive
        user.save()
        user_otp.delete()
        return user
