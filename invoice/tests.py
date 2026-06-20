from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from user.models import User
from tag.models import AdminTag
from lookup.models import Lookup
from invoice.models import Invoice
from decimal import Decimal

class InvoiceTests(APITestCase):
    def setUp(self):
        # Create roles
        self.vendor_role = Lookup.objects.create(name='role', value='Vendor')
        self.buyer_role = Lookup.objects.create(name='role', value='Buyer')
        
        # Create users
        self.vendor = User.objects.create_user(
            email='vendor@example.com',
            password='password123',
            role=self.vendor_role
        )
        self.buyer = User.objects.create_user(
            email='buyer@example.com',
            password='password123',
            role=self.buyer_role
        )
        
        # Create tag
        self.tag = AdminTag.objects.create(tagname='Test Tag')
        
        self.invoice_url = reverse('invoice-list')

    @patch('invoice.views.async_to_sync')
    @patch('invoice.views.get_channel_layer')
    def test_create_invoice_as_vendor(self, mock_get_channel_layer, mock_async_to_sync):
        """
        Ensure we can create a new invoice object as a Vendor.
        """
        self.client.force_authenticate(user=self.vendor)
        data = {
            'buyer': self.buyer.id,
            'tag': self.tag.id,
            'address': '123 Test St',
            'phone_number': '1234567890',
            'price_per_piece': '10.50',
            'quantity': 2,
        }
        
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invoice.objects.count(), 1)
        invoice = Invoice.objects.get()
        self.assertEqual(invoice.vendor, self.vendor)
        self.assertEqual(invoice.buyer, self.buyer)
        self.assertEqual(invoice.total_price, Decimal('21.00')) # 10.50 * 2
        
        # Verify websocket notification
        self.assertTrue(mock_get_channel_layer.called)
        self.assertTrue(mock_async_to_sync.called)

    def test_create_invoice_without_quantity_price_fails(self):
        self.client.force_authenticate(user=self.vendor)
        data = {
            'buyer': self.buyer.id,
            'tag': self.tag.id,
        }
        
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price_per_piece', response.data)

    def test_vendor_gets_own_sent_invoices(self):
        # Create invoices
        invoice1 = Invoice.objects.create(
            vendor=self.vendor, buyer=self.buyer, tag=self.tag,
            price_per_piece=Decimal('10.00'), quantity=1, total_price=Decimal('10.00')
        )
        
        # Create another vendor and invoice
        vendor2 = User.objects.create_user(email='vendor2@example.com', password='pw', role=self.vendor_role)
        Invoice.objects.create(
            vendor=vendor2, buyer=self.buyer, tag=self.tag,
            price_per_piece=Decimal('20.00'), quantity=1, total_price=Decimal('20.00')
        )
        
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get(self.invoice_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['id']), str(invoice1.id))

    def test_buyer_gets_own_received_invoices(self):
        # Create invoices
        invoice1 = Invoice.objects.create(
            vendor=self.vendor, buyer=self.buyer, tag=self.tag,
            price_per_piece=Decimal('10.00'), quantity=1, total_price=Decimal('10.00')
        )
        
        # Create another buyer and invoice
        buyer2 = User.objects.create_user(email='buyer2@example.com', password='pw', role=self.buyer_role)
        Invoice.objects.create(
            vendor=self.vendor, buyer=buyer2, tag=self.tag,
            price_per_piece=Decimal('20.00'), quantity=1, total_price=Decimal('20.00')
        )
        
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.invoice_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['id']), str(invoice1.id))
