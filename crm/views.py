from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from user.models import User
from .serializers import VendorSerializer

class VendorListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all users where the role's value is 'Vendor'
        vendors = User.objects.filter(role__value='Vendor')
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

class BuyerListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all users where the role's value is 'Buyer'
        buyers = User.objects.filter(role__value='Buyer')
        # We can reuse the VendorSerializer since it just serializes the User model with all fields
        serializer = VendorSerializer(buyers, many=True)
        return Response(serializer.data)
