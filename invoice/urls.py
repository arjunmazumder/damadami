from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, ShortNoteViewSet, ConfirmDeliveryView

router = DefaultRouter()
router.register(r'short-notes', ShortNoteViewSet, basename='short-note')
router.register(r'', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('confirm-delivery/', ConfirmDeliveryView.as_view(), name='confirm-delivery'),
    path('', include(router.urls)),
]
