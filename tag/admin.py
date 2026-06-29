from django.contrib import admin
from .models import AdminTag, VendorTag

@admin.register(AdminTag)
class AdminTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tagname', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['tagname']

@admin.register(VendorTag)
class VendorTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'admin_tag', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['vendor__email', 'admin_tag__tagname']
