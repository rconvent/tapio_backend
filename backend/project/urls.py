"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    re_path("^api/schema/$", SpectacularAPIView.as_view(), name="schema"),
    re_path("^api/swagger/$", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    re_path("^api/redoc/$", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    re_path(r"^auth/", include("rest_registration.api.urls")),
    re_path(r"^", include("tapio.urls")),
]
