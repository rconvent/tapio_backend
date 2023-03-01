from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import (
    TokenAuthentication as DefaultTokenAuthentication,
)


# modify the default TokenAuthentication to add select_related profile field
class TokenAuthentication(DefaultTokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            user = get_user_model()._default_manager.select_related("auth_token").get(auth_token__key=key)
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return (user, user.auth_token)


class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# OpenAPI extension to tell swagger how to handle with these
class CsrfExemptSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "project.authentication.CsrfExemptSessionAuthentication"  # full import path OR class ref
    name = "csrfExemptCookieAuth"  # name used in the schema
    priority = -1

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "Session",
        }
