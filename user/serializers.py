from rest_framework import serializers
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'permanent_address', 'present_address', 'phone_number', 'image', 'role', 'is_active', 'is_staff']



from lookup.models import Lookup
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.PrimaryKeyRelatedField(
        queryset=Lookup.objects.filter(name='role', is_active=True),
        required=False,
        allow_null=True,
    )
    image = serializers.ImageField(
        required=False,  # ← optional
        allow_null=True, # ← null দিলেও চলবে
    )

    class Meta:
        model  = User
        fields = [
            'email', 'password', 'confirm_password', 'name',
            'permanent_address', 'present_address',
            'phone_number', 'image', 'role',
        ]

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user     = User(**validated_data)
        user.set_password(password)
        # We don't save the user here since the service handles it. Wait, the RegisterView calls AuthenticationService.register. 
        # But wait! I see RegisterSerializer has a create method but RegisterView does not use it!
        user.save()
        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class EmailOnlySerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data