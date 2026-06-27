from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from user.models import User
from crm.models import Percentage
from .serializers import VendorSerializer, PercentageSerializer, TransactionSerializer

class VendorListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all users where the role's value is 'Vendor'
        vendors = User.objects.filter(role__value='Vendor')
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

class BuyerListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all users where the role's value is 'Buyer'
        buyers = User.objects.filter(role__value='Buyer')
        # We can reuse the VendorSerializer since it just serializes the User model with all fields
        serializer = VendorSerializer(buyers, many=True)
        return Response(serializer.data)

class PercentageViewSet(viewsets.ModelViewSet):
    queryset = Percentage.objects.all()
    serializer_class = PercentageSerializer
    permission_classes = [permissions.IsAuthenticated]

from django.db.models import Sum
from paymentgateway.models import Payment, Payout

class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Extract query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payment_status = request.query_params.get('status', 'SUCCESS')
        payout_status = request.query_params.get('payout_status', 'COMPLETED')

        # Base querysets
        payments_qs = Payment.objects.all()
        payouts_qs = Payout.objects.all()

        # Apply status filters
        if payment_status:
            payments_qs = payments_qs.filter(status=payment_status)
        if payout_status:
            payouts_qs = payouts_qs.filter(status=payout_status)

        # Apply date filters
        if start_date:
            payments_qs = payments_qs.filter(created_at__gte=start_date)
            payouts_qs = payouts_qs.filter(created_at__gte=start_date)
        if end_date:
            # Note: For exact end_date matching, it's often better to add 1 day or use datetime with 23:59:59
            payments_qs = payments_qs.filter(created_at__lte=end_date)
            payouts_qs = payouts_qs.filter(created_at__lte=end_date)

        # 1. Total Commission Earned
        total_commission = payments_qs.aggregate(
            total=Sum('commission_amount')
        )['total'] or 0.00
        
        # 2. Total Vendor Payouts
        total_payout = payouts_qs.aggregate(
            total=Sum('amount')
        )['total'] or 0.00
        
        # 3. Pending Vendor Balances (Always reflects current overall debt)
        pending_balance = User.objects.aggregate(
            total=Sum('wallet_balance')
        )['total'] or 0.00
        
        # 4. Current Commission Percentage
        percentage_obj = Percentage.objects.filter(is_active=True).first()
        current_percentage = percentage_obj.value if percentage_obj else 0.00

        # 5. Total Payment Volume (Total Balance)
        total_balance = payments_qs.aggregate(
            total=Sum('amount')
        )['total'] or 0.00

        data = {
            "total_payment_volume": total_balance,
            "current_commission_percentage": current_percentage,
            "total_commission_earned": total_commission,
            "total_vendor_payouts": total_payout,
            "pending_vendor_balances": pending_balance,
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "payment_status": payment_status,
                "payout_status": payout_status
            }
        }
        return Response(data)



class TransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Extract query parameters for filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status = request.query_params.get('status')
        
        # Base queryset - order by latest
        payments = Payment.objects.all().order_by('-created_at')
        
        if status:
            payments = payments.filter(status=status)
        if start_date:
            payments = payments.filter(created_at__gte=start_date)
        if end_date:
            payments = payments.filter(created_at__lte=end_date)
            
        serializer = TransactionSerializer(payments, many=True)
        return Response(serializer.data)
