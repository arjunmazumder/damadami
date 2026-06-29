from django.contrib import admin
from .models import CallSession

@admin.register(CallSession)
class CallSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'vendor', 'status', 'start_time', 'end_time', 'duration']
    list_filter = ['status']
    search_fields = ['buyer__email', 'vendor__email']
