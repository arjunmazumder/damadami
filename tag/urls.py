from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminTagViewSet, VendorTagViewSet

router = DefaultRouter()
router.register(r'admintags', AdminTagViewSet)
router.register(r'vendortags', VendorTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
