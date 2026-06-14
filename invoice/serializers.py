from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'vendor']

    def validate(self, data):
        # Calculate total_price automatically
        if 'price_per_piece' in data and 'quantity' in data:
            data['total_price'] = data['price_per_piece'] * data['quantity']
        elif 'total_price' not in data and not self.instance:
            raise serializers.ValidationError({"total_price": "Total price is required."})
        return data
