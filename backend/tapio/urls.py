from django.urls import include, re_path
from rest_framework.routers import DefaultRouter
from tapio.viewsets import *

router = DefaultRouter()
router.register(r"report", ReportViewSet)
router.register(r"source", SourceViewSet)
router.register(r"modifiedSource", ModifiedSourceViewSet)
router.register(r"company", CompanyViewSet)
router.register(r"unit", UnitViewSet)

user_router = DefaultRouter()
user_router.register(r"profile", ProfileViewSet)


urlpatterns = [
    re_path(r"api/", include(router.urls)),
    re_path(r"^accounts/", include(user_router.urls))
]

