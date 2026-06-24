from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, ShortNoteViewSet

router = DefaultRouter()
router.register(r'short-notes', ShortNoteViewSet, basename='short-note')
router.register(r'', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
]
