import datetime

import jwt
from django.conf import settings

from NeighborsHub.exceptions import TokenIsNotValidAPIException, TokenExpiredAPIException

JWT_ALGORITHMS = 'HS256'


def generate_email_token(issued_for, user_id, email, expired_at) -> str:
    payload = {
        'issued_for': issued_for,
        'user_id': user_id,
        'email': email,
        'exp': expired_at
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHMS)
    return token


def generate_auth_token(issued_for, user_id) -> str:
    payload = {
        'issued_for': issued_for,
        'user_id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(days=settings.JWT_AUTH_TIME_DELTA)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHMS)
    return token


def verify_custom_token(token: str) -> [bool, dict]:
    """
    response : has_error, result
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHMS])
        return False, {"payload": payload}
    except jwt.ExpiredSignatureError:
        raise TokenIsNotValidAPIException
    except jwt.InvalidTokenError:
        raise TokenExpiredAPIException

