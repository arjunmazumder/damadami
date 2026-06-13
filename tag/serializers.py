from rest_framework import serializers
from .models import AdminTag, VendorTag

class AdminTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminTag
        fields = '__all__'

class VendorTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTag
        fields = '__all__'
