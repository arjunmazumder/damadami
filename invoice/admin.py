from django.contrib import admin
from .models import ShortNote, Invoice

@admin.register(ShortNote)
class ShortNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'vendor', 'product_name', 'price', 'quantity', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'created_at']
    search_fields = ['buyer__email', 'vendor__email', 'product_name']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'vendor', 'status', 'total_price', 'is_confirm', 'created_at']
    list_filter = ['status', 'is_confirm', 'created_at']
    search_fields = ['buyer__email', 'vendor__email', 'product_name']
