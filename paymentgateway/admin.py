from django.contrib import admin
from .models import Payment, Payout

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['tran_id', 'invoice', 'amount', 'status', 'commission_amount', 'vendor_earning', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['tran_id', 'invoice__invoice_id', 'invoice__buyer__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'amount', 'reference_id', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['vendor__email', 'reference_id']
    readonly_fields = ['created_at', 'updated_at']
