from django.contrib import admin
from .models import Lookup

@admin.register(Lookup)
class LookupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'value', 'is_active', 'created_at']
    list_filter = ['name', 'is_active']
    search_fields = ['name', 'value']
