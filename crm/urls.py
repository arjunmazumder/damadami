from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorListView, BuyerListView, PercentageViewSet, DashboardSummaryView, TransactionListView

router = DefaultRouter()
router.register(r'percentages', PercentageViewSet, basename='percentage')

urlpatterns = [
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('buyers/', BuyerListView.as_view(), name='buyer-list'),
    path('dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('', include(router.urls)),
]
