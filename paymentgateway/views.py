import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from sslcommerz_lib import SSLCOMMERZ
from invoice.models import Invoice
from .models import Payment

class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="InitiatePaymentRequest",
            fields={
                "invoice_id": serializers.UUIDField(),
                "phone_number": serializers.CharField(required=True, help_text="Contact number for this payment"),
                "address": serializers.CharField(required=True, help_text="Delivery or billing address")
            }
        ),
        responses={200: inline_serializer(
            name="InitiatePaymentResponse",
            fields={
                "GatewayPageURL": serializers.URLField()
            }
        )}
    )
    def post(self, request):
        invoice_id = request.data.get('invoice_id')
        phone_number = request.data.get('phone_number')
        address = request.data.get('address')
        
        if not invoice_id or not phone_number or not address:
            return Response({"error": "invoice_id, phone_number, and address are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        if invoice.buyer != request.user:
            return Response({"error": "You can only pay for your own invoices"}, status=status.HTTP_403_FORBIDDEN)
            
        if invoice.status == 'paid':
            return Response({"error": "Invoice is already paid"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a pending Payment record
        tran_id = str(uuid.uuid4())
        Payment.objects.create(
            invoice=invoice,
            tran_id=tran_id,
            amount=invoice.total_price,
            status='PENDING'
        )

        settings_dict = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_pass': settings.SSLCOMMERZ_STORE_PASS,
            'issandbox': settings.SSLCOMMERZ_IS_SANDBOX
        }
        sslcz = SSLCOMMERZ(settings_dict)

        # Build callback URLs
        # In production, use your actual domain instead of 127.0.0.1
        base_url = "http://127.0.0.1:8001/payment"
        post_body = {}
        post_body['total_amount'] = float(invoice.total_price)
        post_body['currency'] = "BDT"
        post_body['tran_id'] = tran_id
        post_body['success_url'] = f"{base_url}/success/"
        post_body['fail_url'] = f"{base_url}/fail/"
        post_body['cancel_url'] = f"{base_url}/cancel/"
        post_body['emi_option'] = 0
        post_body['cus_name'] = request.user.name or request.user.email
        post_body['cus_email'] = request.user.email
        post_body['cus_phone'] = phone_number
        post_body['cus_add1'] = address
        post_body['cus_city'] = "Dhaka"
        post_body['cus_country'] = "Bangladesh"
        post_body['shipping_method'] = "NO"
        post_body['multi_card_name'] = ""
        post_body['num_of_item'] = invoice.quantity
        post_body['product_name'] = invoice.tag.tagname if invoice.tag else "Product"
        post_body['product_category'] = "General"
        post_body['product_profile'] = "general"

        response = sslcz.createSession(post_body)
        
        if response.get('status') == 'SUCCESS':
            return Response({"GatewayPageURL": response['GatewayPageURL']})
        else:
            return Response({"error": "Failed to initiate payment with SSLCommerz"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        tran_id = data.get('tran_id')
        val_id = data.get('val_id')
        
        if not tran_id or not val_id:
            return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
            
        settings_dict = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_pass': settings.SSLCOMMERZ_STORE_PASS,
            'issandbox': settings.SSLCOMMERZ_IS_SANDBOX
        }
        sslcz = SSLCOMMERZ(settings_dict)
        validation_response = sslcz.validationTransactionOrder(val_id)
        
        if validation_response and isinstance(validation_response, dict):
            status_val = validation_response.get('status')
            if status_val == 'VALID' or status_val == 'VALIDATED':
                try:
                    payment = Payment.objects.get(tran_id=tran_id)
                    payment.status = 'SUCCESS'
                    payment.val_id = val_id
                    payment.save()
                    
                    invoice = payment.invoice
                    invoice.status = 'paid'
                    invoice.save()
                    
                    return Response({
                        "message": "Payment Successful. You can close this page.",
                        "payment_details": {
                            "invoice_id": invoice.id,
                            "transaction_id": payment.tran_id,
                            "validation_id": payment.val_id,
                            "amount": payment.amount,
                            "status": payment.status,
                            "buyer": {
                                "id": invoice.buyer.id,
                                "email": invoice.buyer.email
                            }
                        }
                    })
                except Payment.DoesNotExist:
                    return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"error": "Payment Validation Failed or Invalid Response"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentFailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        tran_id = request.data.get('tran_id')
        try:
            payment = Payment.objects.get(tran_id=tran_id)
            payment.status = 'FAILED'
            payment.save()
            return Response({
                "message": "Payment Failed!",
                "payment_details": {
                    "invoice_id": payment.invoice.id,
                    "transaction_id": payment.tran_id,
                    "amount": payment.amount,
                    "status": payment.status,
                    "buyer": {
                        "id": payment.invoice.buyer.id,
                        "email": payment.invoice.buyer.email
                    }
                }
            })
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

class PaymentCancelView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        tran_id = request.data.get('tran_id')
        try:
            payment = Payment.objects.get(tran_id=tran_id)
            payment.status = 'CANCELLED'
            payment.save()
            return Response({
                "message": "Payment Cancelled!",
                "payment_details": {
                    "invoice_id": payment.invoice.id,
                    "transaction_id": payment.tran_id,
                    "amount": payment.amount,
                    "status": payment.status,
                    "buyer": {
                        "id": payment.invoice.buyer.id,
                        "email": payment.invoice.buyer.email
                    }
                }
            })
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

from .models import Payout
from user.models import User
from decimal import Decimal

class AdminMarkAsPaidView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        responses={200: inline_serializer(
            name="AdminPayoutListResponse",
            fields={
                "id": serializers.UUIDField(),
                "vendor_name": serializers.CharField(),
                "vendor_email": serializers.EmailField(),
                "amount": serializers.DecimalField(max_digits=10, decimal_places=2),
                "reference_id": serializers.CharField(),
                "note": serializers.CharField(),
                "status": serializers.CharField(),
                "created_at": serializers.DateTimeField()
            },
            many=True
        )}
    )
    def get(self, request):
        payouts = Payout.objects.select_related('vendor').all().order_by('-created_at')
        data = []
        for p in payouts:
            data.append({
                "id": p.id,
                "vendor_name": p.vendor.name if p.vendor else None,
                "vendor_email": p.vendor.email if p.vendor else None,
                "amount": p.amount,
                "reference_id": p.reference_id,
                "note": p.note,
                "status": p.status,
                "created_at": p.created_at
            })
        return Response(data)

    @extend_schema(
        request=inline_serializer(
            name="AdminMarkAsPaidRequest",
            fields={
                "vendor_name": serializers.CharField(),
                "amount": serializers.DecimalField(max_digits=10, decimal_places=2),
                "reference_id": serializers.CharField(required=False, help_text="Bank/Bkash TrxID"),
                "note": serializers.CharField(required=False, help_text="Optional note regarding the payout"),
            }
        ),
        responses={200: inline_serializer(
            name="AdminMarkAsPaidResponse",
            fields={
                "message": serializers.CharField()
            }
        )}
    )
    def post(self, request):
        vendor_name = request.data.get('vendor_name')
        amount = request.data.get('amount')
        reference_id = request.data.get('reference_id', '')
        note = request.data.get('note', '')

        if not vendor_name or amount is None:
            return Response({"error": "vendor_name and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

        vendor = User.objects.filter(name=vendor_name).first()
        if not vendor:
            vendor = User.objects.filter(email=vendor_name).first()
            
        if not vendor:
            return Response({"error": "Vendor not found with the given name"}, status=status.HTTP_404_NOT_FOUND)

        if amount > vendor.wallet_balance:
            return Response({"error": f"Cannot payout more than available balance ({vendor.wallet_balance})"}, status=status.HTTP_400_BAD_REQUEST)

        Payout.objects.create(
            vendor=vendor,
            amount=amount,
            reference_id=reference_id,
            status='COMPLETED',
            note=note
        )

        return Response({"message": f"Successfully marked {amount} as paid to {vendor.email}."})

