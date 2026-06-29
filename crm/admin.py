from django.contrib import admin
from .models import Percentage

@admin.register(Percentage)
class PercentageAdmin(admin.ModelAdmin):
    list_display = ['value', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
