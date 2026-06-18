from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, VerifyOTPSerializer, EmailOnlySerializer, ResetPasswordSerializer
from .services import AuthenticationService
from .models import User

class VerifyOTPView(APIView):
    permission_classes = []
    
    @extend_schema(
        request=VerifyOTPSerializer,
        responses={200: inline_serializer(
            name='VerifyOTPResponse',
            fields={'success': serializers.BooleanField(), 'message': serializers.CharField()}
        )},
        description="Verify OTP to activate user account"
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            AuthenticationService.verify_otp(
                email=serializer.validated_data['email'],
                otp=serializer.validated_data['otp']
            )
        except ValueError as e:
            return Response(
                {'success': False, 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {'success': True, 'message': 'Account successfully verified'},
            status=status.HTTP_200_OK
        )

class ForgotPasswordView(APIView):
    permission_classes = []
    
    @extend_schema(
        request=EmailOnlySerializer,
        responses={200: inline_serializer(
            name='ForgotPasswordResponse',
            fields={'success': serializers.BooleanField(), 'message': serializers.CharField()}
        )},
        description="Send password reset OTP to email"
    )
    def post(self, request):
        serializer = EmailOnlySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            AuthenticationService.forgot_password(email=serializer.validated_data['email'])
        except ValueError as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'success': True, 'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

class ResendOTPView(APIView):
    permission_classes = []
    
    @extend_schema(
        request=EmailOnlySerializer,
        responses={200: inline_serializer(
            name='ResendOTPResponse',
            fields={'success': serializers.BooleanField(), 'message': serializers.CharField()}
        )},
        description="Resend OTP to email"
    )
    def post(self, request):
        serializer = EmailOnlySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            AuthenticationService.resend_otp(email=serializer.validated_data['email'])
        except ValueError as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'success': True, 'message': 'New OTP sent successfully'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = []
    
    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: inline_serializer(
            name='ResetPasswordResponse',
            fields={'success': serializers.BooleanField(), 'message': serializers.CharField()}
        )},
        description="Reset password using OTP"
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            AuthenticationService.reset_password(
                email=serializer.validated_data['email'],
                otp=serializer.validated_data['otp'],
                new_password=serializer.validated_data['new_password']
            )
        except ValueError as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'success': True, 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = []
    parser_classes     = [MultiPartParser, FormParser, JSONParser]  # ← এটাই missing ছিল

    @extend_schema(
        request=RegisterSerializer,
        responses={201: inline_serializer(
            name='RegisterResponse',
            fields={'user': UserSerializer()}
        )},
        description="Register a new user"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            print("Registration Validation Errors:", serializer.errors)  # ← Added to help you debug what frontend sent wrong
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data.copy()
            email    = validated_data.pop('email')
            password = validated_data.pop('password')
            validated_data.pop('confirm_password', None) # ← Fixed here
            user     = AuthenticationService.register(
                email=email,
                password=password,
                **validated_data
            )
        except ValueError as e:
            return Response(
                {'success': False, 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'success': True, 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={200: inline_serializer(
            name='LoginResponse',
            fields={
                'access_token': serializers.CharField(),
                'user': UserSerializer()
            }
        )},
        description="Login to get access token and refresh token cookie"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            access_token, refresh_token, user = AuthenticationService.login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
        except ValueError as e:
            return Response(
                {'success': False, 'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response(
            {'success': True, 'access_token': access_token, 'user': UserSerializer(user).data},
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=not getattr(settings, 'DEBUG', True),
            samesite='Lax'
        )
        return response


class RefreshView(APIView):
    permission_classes = []

    @extend_schema(
        request=None,
        responses={200: inline_serializer(
            name='RefreshResponse',
            fields={'access_token': serializers.CharField()}
        )},
        description="Get a new access token using the refresh token cookie"
    )
    def post(self, request):
        old_refresh_token = request.COOKIES.get('refresh_token')

        if not old_refresh_token:
            return Response(
                {'success': False, 'detail': 'Refresh token পাওয়া যায়নি।'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            new_access_token, new_refresh_token = AuthenticationService.refresh_token(old_refresh_token)
        except ValueError as e:
            return Response(
                {'success': False, 'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response(
            {'success': True, 'access_token': new_access_token},
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=not getattr(settings, 'DEBUG', True),
            samesite='Lax'
        )
        return response


class LogoutView(APIView):
    permission_classes = []

    @extend_schema(
        request=None,
        responses={200: inline_serializer(
            name='LogoutResponse',
            fields={'message': serializers.CharField()}
        )},
        description="Logout and clear the refresh token cookie"
    )
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        AuthenticationService.logout(refresh_token)

        response = Response(
            {'success': True, 'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('refresh_token')
        return response


@extend_schema(tags=['users'])
class UserListView(generics.ListAPIView):
    permission_classes = []
    queryset           = User.objects.all()
    serializer_class   = UserSerializer