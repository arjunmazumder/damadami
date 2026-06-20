from rest_framework import viewsets, permissions
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Invoice
from .serializers import InvoiceSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user.role, 'value', '') == 'Vendor':
            return Invoice.objects.filter(vendor=user)
        return Invoice.objects.filter(buyer=user)

    def perform_create(self, serializer):
        invoice = serializer.save(vendor=self.request.user)
        
        # Send real-time notification to buyer
        channel_layer = get_channel_layer()
        group_name = f"buyer_{invoice.buyer.id}"
        
        message_data = {
            'type': 'new_invoice',
            'invoice_id': str(invoice.id),
            'vendor_name': invoice.vendor.name or invoice.vendor.email,
            'tag_name': invoice.tag.tagname if invoice.tag else None,
            'price_per_piece': str(invoice.price_per_piece),
            'quantity': invoice.quantity,
            'total_price': str(invoice.total_price),
            'status': invoice.status
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            message_data
        )
