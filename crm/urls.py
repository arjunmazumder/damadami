from django.urls import path
from .views import VendorListView, BuyerListView

urlpatterns = [
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('buyers/', BuyerListView.as_view(), name='buyer-list'),
]
