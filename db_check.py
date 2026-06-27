import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damadami.settings')
django.setup()

from user.models import User
from invoice.models import Invoice
from paymentgateway.models import Payment, Payout
from crm.models import Percentage

print('--- DATABASE CHECK ---')
print(f'Total Users: {User.objects.count()}')
print(f'Vendors: {User.objects.filter(role__value="Vendor").count()}')
print(f'Buyers: {User.objects.filter(role__value="Buyer").count()}')

active_pct = Percentage.objects.filter(is_active=True).first()
print(f'Active Commission Percentage: {active_pct.value if active_pct else "None"}%')

print(f'\nTotal Invoices: {Invoice.objects.count()}')
for inv in Invoice.objects.all()[:3]:
    print(f' - ID: {inv.id}, Vendor: {inv.vendor.email}, Buyer: {inv.buyer.email}, Status: {inv.status}, Total: {inv.total_price}')

print(f'\nTotal Payments: {Payment.objects.count()}')
success_payments = Payment.objects.filter(status="SUCCESS")
print(f'Success Payments: {success_payments.count()}')
for p in success_payments[:3]:
    print(f' - ID: {p.id}, Amount: {p.amount}, Comm: {p.commission_amount}, Earning: {p.vendor_earning}')

print(f'\nTotal Payouts: {Payout.objects.count()}')

print('\nVendor Wallet Balances (Top 3 with balance > 0):')
for u in User.objects.filter(wallet_balance__gt=0)[:3]:
    print(f' - Vendor: {u.email}, Wallet Balance: {u.wallet_balance}')

print('----------------------')
