from django.contrib import admin
from .models import User, UserSession, UserOTP, VendorPayoutMethod

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'phone_number', 'wallet_balance', 'is_active']
    list_filter = ['is_superuser', 'is_active', 'role']
    search_fields = ['email', 'name', 'phone_number']

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'expires_at', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email']

@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'created_at']
    search_fields = ['user__email']

@admin.register(VendorPayoutMethod)
class VendorPayoutMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank_name', 'account_name', 'account_number', 'created_at']
    search_fields = ['user__email', 'bank_name', 'account_number']
