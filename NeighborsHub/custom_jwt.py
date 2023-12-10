import jwt
from django.conf import settings

JWT_ALGORITHMS = 'HS256'


def generate_email_token(issued_for, user_id, email, expired_at):
    payload = {
        'issued_for': issued_for,
        'user_id': user_id,
        'email': email,
        'exp': expired_at
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHMS)
    return token


def verify_custom_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHMS])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired.'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token.'}
