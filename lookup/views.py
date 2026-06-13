from rest_framework import viewsets
from .models import Lookup
from .serializers import LookupSerializer

class LookupViewSet(viewsets.ModelViewSet):
    queryset = Lookup.objects.all()
    serializer_class = LookupSerializer

