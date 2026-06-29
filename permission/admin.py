from django.contrib import admin
from .models import Permission

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'permission_name', 'status', 'create_at']
    list_filter = ['status', 'role']
    search_fields = ['permission_name']
