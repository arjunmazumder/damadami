from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer
from .services import AuthenticationService

class RegisterView(APIView):
    permission_classes = [] # Allow any
    
    @extend_schema(
        request=RegisterSerializer,
        responses={201: inline_serializer(
           name='RegisterResponse',
           fields={
               'user': UserSerializer()
           }
        )},
        description="Register a new user"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            validated_data = serializer.validated_data.copy()
            email = validated_data.pop('email')
            password = validated_data.pop('password')
            user = AuthenticationService.register(
                email=email,
                password=password,
                **validated_data
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        user_data = UserSerializer(user).data
        return Response({"user": user_data}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [] # Allow any
    
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            access_token, refresh_token, user = AuthenticationService.login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        user_data = UserSerializer(user).data
        
        response = Response({
            "access_token": access_token,
            "user": user_data
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=not getattr(settings, 'DEBUG', True), # True in production
            samesite='Lax'
        )
        
        return response

class RefreshView(APIView):
    permission_classes = [] # Allow any
    
    @extend_schema(
        request=None,
        responses={200: inline_serializer(
           name='RefreshResponse',
           fields={
               'access_token': serializers.CharField()
           }
        )},
        description="Get a new access token using the refresh token cookie"
    )
    def post(self, request):
        old_refresh_token = request.COOKIES.get('refresh_token')
        
        try:
            new_access_token, new_refresh_token = AuthenticationService.refresh_token(old_refresh_token)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        response = Response({
            "access_token": new_access_token
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=not getattr(settings, 'DEBUG', True),
            samesite='Lax'
        )
        
        return response

class LogoutView(APIView):
    permission_classes = [] # Allow any
    
    @extend_schema(
        request=None,
        responses={200: inline_serializer(
           name='LogoutResponse',
           fields={
               'message': serializers.CharField()
           }
        )},
        description="Logout and clear the refresh token cookie"
    )
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        AuthenticationService.logout(refresh_token)
        
        response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        
        return response

from rest_framework import generics
from .models import User

@extend_schema(tags=['users'])
class UserListView(generics.ListAPIView):
    permission_classes = [] 
    queryset = User.objects.all()
    serializer_class = UserSerializer
