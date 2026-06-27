from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Permission
from .serializers import PermissionSerializer
from .custom_permissions import RoleBasedPermission
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['permissions'])
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
