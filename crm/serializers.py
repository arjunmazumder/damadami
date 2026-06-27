from rest_framework import serializers
from user.models import User

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

from crm.models import Percentage

class PercentageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Percentage
        fields = '__all__'
from paymentgateway.models import Payment

class TransactionSerializer(serializers.ModelSerializer):
    vendor_name = serializers.SerializerMethodField()
    commission_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'tran_id', 'vendor_name', 'amount', 
            'commission_percentage', 'commission_amount', 
            'vendor_earning', 'created_at', 'status'
        ]

    def get_vendor_name(self, obj):
        if obj.invoice and obj.invoice.vendor:
            return obj.invoice.vendor.name or obj.invoice.vendor.email
        return "Unknown"

    def get_commission_percentage(self, obj):
        if obj.amount > 0 and obj.commission_amount > 0:
            return round((obj.commission_amount / obj.amount) * 100, 2)
        return 0.00
