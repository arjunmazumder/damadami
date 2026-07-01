from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AdminTag, VendorTag, Category
from .serializers import AdminTagSerializer, VendorTagSerializer, CategorySerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def tags(self, request, pk=None):
        category = self.get_object()
        active_tags = category.tags.filter(is_active=True)
        serializer = AdminTagSerializer(active_tags, many=True)
        return Response(serializer.data)

@extend_schema(tags=['admin_tags'])
class AdminTagViewSet(viewsets.ModelViewSet):
    queryset = AdminTag.objects.all()
    serializer_class = AdminTagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['tagname']

    @action(detail=False, methods=['get'])
    def trending(self, request):
        trending_tags = self.get_queryset().filter(is_trending=True, is_active=True)
        serializer = self.get_serializer(trending_tags, many=True)
        return Response(serializer.data)

@extend_schema(tags=['vendor_tags'])
class VendorTagViewSet(viewsets.ModelViewSet):
    queryset = VendorTag.objects.all()
    serializer_class = VendorTagSerializer
