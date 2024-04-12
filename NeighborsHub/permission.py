from channels.auth import AuthMiddlewareStack
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission

from NeighborsHub.custom_jwt import verify_custom_token
from NeighborsHub.redis_management import AuthenticationTokenRedis
from users.models import CustomerUser, Address
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


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


class IsVerifiedUserPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_verified_email or request.user.is_verified_mobile


class TokenAuthMiddlewareChannels(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    @staticmethod
    def get_user(user_id):
        try:
            user = CustomerUser.objects.get(id=user_id)
            return user
        except CustomerUser.DoesNotExist:
            return None

    @staticmethod
    def _check_token_in_redis(token, user_id):
        redis_user = AuthenticationTokenRedis().get(token)
        if redis_user is None or int(user_id) != int(redis_user):
            raise exceptions.AuthenticationFailed(_('Token is not valid'))
        return True

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None

        has_error, payload = verify_custom_token(token_key) if token_key is not None else (True, None)
        if has_error:
            raise exceptions.AuthenticationFailed()
        self._check_token_in_redis(token_key, payload['payload']['user_id'])
        if token_key is None:
            scope['user'] = AnonymousUser()
        else:
            scope['user'] = await database_sync_to_async(self.get_user)(payload['payload']['user_id'])
        return await super().__call__(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddlewareChannels(AuthMiddlewareStack(inner))
