from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model

from rest_framework import exceptions
from NeighborsHub.custom_jwt import verify_custom_token
from NeighborsHub.redis_management import AuthenticationTokenRedis
from django.utils.translation import gettext as _


class TokenAuthMiddlewareChannels(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    @staticmethod
    def get_user(user_id):
        try:
            user = get_user_model().objects.get(id=user_id)
            return user
        except get_user_model().DoesNotExist:
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
            scope['user'] = None
        else:
            scope['user'] = await database_sync_to_async(self.get_user)(payload['payload']['user_id'])
            print(scope['user'])
        return await super().__call__(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddlewareChannels(AuthMiddlewareStack(inner))
