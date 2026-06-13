from rest_framework import viewsets
from .models import Permission
from .serializers import PermissionSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['permissions'])
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
