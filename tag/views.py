from rest_framework import viewsets, filters
from .models import AdminTag, VendorTag
from .serializers import AdminTagSerializer, VendorTagSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['admin_tags'])
class AdminTagViewSet(viewsets.ModelViewSet):
    queryset = AdminTag.objects.all()
    serializer_class = AdminTagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['tagname']

@extend_schema(tags=['vendor_tags'])
class VendorTagViewSet(viewsets.ModelViewSet):
    queryset = VendorTag.objects.all()
    serializer_class = VendorTagSerializer
