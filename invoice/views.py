from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from livesession.models import CallSession
from .models import Invoice, ShortNote
from .serializers import InvoiceSerializer, ShortNoteSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user.role, 'value', '') == 'Admin':
            return Invoice.objects.all()
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
            'product_name': invoice.product_name,
            'short_note_id': str(invoice.short_note.id) if invoice.short_note else None,
            'is_confirm': invoice.is_confirm,
            'price_per_piece': str(invoice.price_per_piece),
            'quantity': invoice.quantity,
            'total_price': str(invoice.total_price),
            'status': invoice.status
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            message_data
        )

class ShortNoteViewSet(viewsets.ModelViewSet):
    queryset = ShortNote.objects.all()
    serializer_class = ShortNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user.role, 'value', '') == 'Admin':
            return ShortNote.objects.all()
        if getattr(user.role, 'value', '') == 'Vendor':
            return ShortNote.objects.filter(vendor=user)
        return ShortNote.objects.filter(buyer=user)

    def perform_create(self, serializer):
        user = self.request.user
        
        # Ensure only buyer can create a short note during call
        if getattr(user.role, 'value', '') != 'Buyer':
            raise ValidationError({"error": "Only buyers can create a short note."})
        
        # Find active session for the buyer
        session = CallSession.objects.filter(buyer=user, status='connected').first()
        if not session:
            raise ValidationError({"error": "No active connected call session found for the buyer."})
        
        serializer.save(
            session=session,
            channel_name=session.channel_name,
            buyer=user,
            vendor=session.vendor,
            tag=session.tag
        )
