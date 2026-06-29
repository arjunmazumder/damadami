from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorListView, VendorDetailView, BuyerListView, BuyerDetailView, PercentageViewSet, DashboardSummaryView, TransactionListView, VendorPayoutListView

router = DefaultRouter()
router.register(r'percentages', PercentageViewSet, basename='percentage')

urlpatterns = [
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<uuid:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('buyers/', BuyerListView.as_view(), name='buyer-list'),
    path('buyers/<uuid:pk>/', BuyerDetailView.as_view(), name='buyer-detail'),
    path('dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('vendorpayout/', VendorPayoutListView.as_view(), name='vendorpayout-list'),
    path('', include(router.urls)),
]
