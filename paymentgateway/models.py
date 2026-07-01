import uuid
from django.db import models
from invoice.models import Invoice

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    tran_id = models.CharField(max_length=100, unique=True, help_text="Transaction ID")
    val_id = models.CharField(max_length=100, blank=True, null=True, help_text="Validation ID from SSLCommerz")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Platform Commission")
    vendor_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount for the vendor")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.tran_id} - {self.status}"

class Payout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    trx_id = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction ID")
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    note = models.TextField(blank=True, null=True, help_text="Optional note regarding the payout")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payout {self.id} for {self.vendor.email} - {self.status}"
