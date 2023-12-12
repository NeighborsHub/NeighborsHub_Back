from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext as _


class TokenIsNotValidAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Token is not valid')


class TokenExpiredAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Token expired')
