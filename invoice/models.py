import uuid
from django.db import models
from user.models import User
from tag.models import AdminTag





class ShortNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('livesession.CallSession', on_delete=models.CASCADE, related_name='short_notes')
    channel_name = models.CharField(max_length=255)
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_short_notes')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_short_notes')
    tag = models.ForeignKey(AdminTag, on_delete=models.SET_NULL, null=True, blank=True, related_name='short_notes')
    product_name = models.CharField(max_length=255, default='Unknown')
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    note = models.TextField(blank=True, null=True)
    
    is_processed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ShortNote {self.id} - Vendor: {self.vendor.email} - Processed: {self.is_processed}"




class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invoices')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invoices')
    tag = models.ForeignKey(AdminTag, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    # Invoice Details
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Pricing
    price_per_piece = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional Details
    product_name = models.CharField(max_length=255, blank=True, null=True)
    short_note = models.ForeignKey(ShortNote, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    is_confirm = models.BooleanField(default=False)
    buyer_confirmed_delivery = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.id} - Vendor: {self.vendor.email}"

