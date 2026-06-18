from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Lookup
from .serializers import LookupSerializer

class LookupViewSet(viewsets.ModelViewSet):
    queryset = Lookup.objects.all()
    serializer_class = LookupSerializer

    @action(detail=False, methods=['get'])
    def roles(self, request):
        roles = Lookup.objects.filter(name='role', is_active=True).values('id', 'value')
        return Response(roles)
