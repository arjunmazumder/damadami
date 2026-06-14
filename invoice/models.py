import uuid
from django.db import models
from user.models import User
from tag.models import AdminTag

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
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
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.id} - Vendor: {self.vendor.email}"
