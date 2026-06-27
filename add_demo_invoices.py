import os
import django
import random
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damadami.settings')
django.setup()

from user.models import User
from invoice.models import Invoice

def create_demo_invoices():
    # Try to get or create some users
    buyer, created = User.objects.get_or_create(email='buyer@demo.com')
    if created:
        buyer.set_password('demo123')
        buyer.save()
        print("Created buyer: buyer@demo.com")

    vendor, created = User.objects.get_or_create(email='vendor@demo.com')
    if created:
        vendor.set_password('demo123')
        vendor.save()
        print("Created vendor: vendor@demo.com")

    # Create some demo invoices
    demo_products = ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Keyboard']
    statuses = ['pending', 'accepted', 'rejected', 'paid']

    invoices_to_create = []
    for i in range(5):
        product_name = random.choice(demo_products)
        price_per_piece = Decimal(random.randint(500, 5000))
        quantity = random.randint(1, 5)
        total_price = price_per_piece * quantity
        status = random.choice(statuses)

        invoice = Invoice(
            buyer=buyer,
            vendor=vendor,
            address='123 Demo Street, Demo City',
            phone_number='01700000000',
            price_per_piece=price_per_piece,
            quantity=quantity,
            total_price=total_price,
            product_name=product_name,
            status=status
        )
        invoices_to_create.append(invoice)

    Invoice.objects.bulk_create(invoices_to_create)
    print(f"Successfully created {len(invoices_to_create)} demo invoices.")

if __name__ == '__main__':
    create_demo_invoices()
