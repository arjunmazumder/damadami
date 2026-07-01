from django.contrib import admin
from .models import AdminTag, VendorTag, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(AdminTag)
class AdminTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tagname', 'category', 'is_trending', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_trending', 'category', 'created_at']
    search_fields = ['tagname', 'category__name']

@admin.register(VendorTag)
class VendorTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'admin_tag', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['vendor__email', 'admin_tag__tagname']
