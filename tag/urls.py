from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminTagViewSet, VendorTagViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'admintags', AdminTagViewSet)
router.register(r'vendortags', VendorTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
