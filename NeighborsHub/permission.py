from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission

from NeighborsHub.custom_jwt import verify_custom_token
from NeighborsHub.redis_management import AuthenticationTokenRedis
from users.models import CustomerUser, Address


class CustomAuthentication(authentication.BaseAuthentication):
    @staticmethod
    def _check_token_in_redis(token, user_id):
        redis_user = AuthenticationTokenRedis().get(token)
        if redis_user is None or int(user_id) != int(redis_user):
            raise exceptions.AuthenticationFailed(_('Token is not valid'))
        return True

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None or len(token.split()) < 2:
            raise exceptions.AuthenticationFailed(_('Access token is not exist.'))
        has_error, payload = verify_custom_token(token.split()[1])
        if has_error:
            raise exceptions.AuthenticationFailed(_(payload['error']))
        self._check_token_in_redis(token.split()[1], payload['payload']['user_id'])
        try:
            user = get_user_model().objects.get(id=payload['payload']['user_id'])
        except CustomerUser.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('User does not exist'))
        return user, None


class CustomAuthenticationWithoutEffect(CustomAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None, None


class IsOwnerAuthentication(BasePermission):

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Address):
            return obj.user == request.user
        else:
            return obj.created_by == request.user
