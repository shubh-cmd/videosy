from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework import permissions
from rest_framework.authtoken.models import Token


class CheckPermissions(permissions.BasePermission):

    def has_permission(self, request, view):

        auth_token = request.headers.get('Authorization')
        try:
            token = Token.objects.get(key=auth_token)
        except Token.DoesNotExist:
            raise PermissionDenied()  # 403

        request.user = token.user
        return True
