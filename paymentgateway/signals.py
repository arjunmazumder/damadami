from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Payment, Payout
from crm.models import Percentage
from decimal import Decimal

@receiver(pre_save, sender=Payment)
def calculate_payment_commission(sender, instance, **kwargs):
    # Only calculate if the payment is transitioning to SUCCESS and hasn't been processed yet
    # Or simply always calculate commission if it's 0 and amount > 0
    if instance.status == 'SUCCESS' and instance.commission_amount == 0 and instance.vendor_earning == 0:
        # Get active commission percentage
        percentage_obj = Percentage.objects.filter(is_active=True).first()
        commission_rate = percentage_obj.value if percentage_obj else Decimal('0.00')
        
        commission = (instance.amount * commission_rate) / Decimal('100.00')
        vendor_earning = instance.amount - commission
        
        instance.commission_amount = commission
        instance.vendor_earning = vendor_earning

@receiver(post_save, sender=Payment)
def update_vendor_balance_on_payment(sender, instance, created, **kwargs):
    if instance.status == 'SUCCESS':
        # Assuming we only add to wallet once. A more robust system would use a transaction log.
        # For simplicity, we just add the earning if the vendor hasn't been credited.
        # In a real scenario, we should track if this exact payment was already credited.
        vendor = instance.invoice.vendor
        
        # We will assume signal is idempotent for now (in production, use a flag `is_credited`)
        pass # Better to do it in pre_save or with a flag to avoid double credit. 
        # Actually, let's just add a flag to Payment or do it carefully.
        # To make it simple and safe for this demo:
        # We will recalculate the wallet balance from all successful payments and completed payouts.
        recalculate_vendor_wallet(vendor)

@receiver(post_save, sender=Payout)
def update_vendor_balance_on_payout(sender, instance, created, **kwargs):
    if instance.status == 'COMPLETED':
        recalculate_vendor_wallet(instance.vendor)

from django.utils import timezone
from datetime import timedelta
from invoice.models import Invoice

@receiver(post_save, sender=Invoice)
def update_vendor_balance_on_delivery_confirm(sender, instance, created, **kwargs):
    if instance.buyer_confirmed_delivery:
        recalculate_vendor_wallet(instance.vendor)

def recalculate_vendor_wallet(vendor):
    # Sum of all successful vendor earnings
    successful_payments = Payment.objects.filter(
        invoice__vendor=vendor, 
        status='SUCCESS'
    )
    
    total_earned = Decimal('0.00')
    now = timezone.now()
    
    for p in successful_payments:
        # Fund is released if buyer confirmed OR 4 hours have passed since payment
        if p.invoice.buyer_confirmed_delivery or (now - p.updated_at) > timedelta(hours=4):
            total_earned += p.vendor_earning
    
    # Sum of all completed payouts
    completed_payouts = Payout.objects.filter(
        vendor=vendor,
        status='COMPLETED'
    )
    total_paid = sum(p.amount for p in completed_payouts) or Decimal('0.00')
    
    vendor.wallet_balance = total_earned - total_paid
    vendor.save(update_fields=['wallet_balance'])
