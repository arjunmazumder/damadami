from rest_framework import serializers
from .models import AdminTag, VendorTag, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AdminTagSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = AdminTag
        fields = '__all__'

class VendorTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTag
        fields = '__all__'
