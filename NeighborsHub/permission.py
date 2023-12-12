from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import gettext as _

from NeighborsHub.custom_jwt import verify_custom_token
from NeighborsHub.redis_management import AuthenticationTokenRedis


class CustomAuthentication(authentication.BaseAuthentication):
    @staticmethod
    def _check_token_in_redis(token, user_id):
        redis_user = AuthenticationTokenRedis().get(token)
        if redis_user is None or user_id != redis_user:
            raise exceptions.AuthenticationFailed(_('Token is not valid'))
        return True

    def authenticate(self, request):
        token = request.META.get('HTTP_Authorization')
        if token is None or len(token.split())< 2:
            raise exceptions.AuthenticationFailed(_('Access token is not exist.'))
        has_error, payload = verify_custom_token(token.split()[1])
        if has_error:
            raise exceptions.AuthenticationFailed(_(payload['error']))
        self._check_token_in_redis(token[1], payload['user_id'])
        try:
            user = get_user_model().objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('User does not exist'))
        return user, None


