from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include('user.urls')),
    path("lookup/", include('lookup.urls')),
    path("tag/", include('tag.urls')),
    path("permission/", include('permission.urls')),
    path("livesession/", include('livesession.urls')),
    path("invoice/", include('invoice.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
