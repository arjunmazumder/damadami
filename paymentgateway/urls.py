from django.urls import path
from .views import InitiatePaymentView, PaymentSuccessView, PaymentFailView, PaymentCancelView, AdminMarkAsPaidView

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('fail/', PaymentFailView.as_view(), name='payment-fail'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('admin/mark-as-paid/', AdminMarkAsPaidView.as_view(), name='admin-mark-as-paid'),
]
