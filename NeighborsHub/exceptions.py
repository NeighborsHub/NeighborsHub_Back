from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext as _
from rest_framework.views import exception_handler


class CustomException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = _('err')
    default_detail = _('Error')

    def handle_custom_exception(self):
        response_data = {
            'status': 'error',
            'message': str(self.default_detail),
            'code': str(self.default_code)
        }
        return Response(response_data, status=self.status_code)


def custom_exception_handler(exc, context):
    if isinstance(exc, CustomException):
        return exc.handle_custom_exception()
    response = exception_handler(exc, context)
    response_data = {
        'status': 'error',
        'message': exc.default_detail,
        'data': response.data,
        'code': ''
    }
    return Response(status=response.status_code, data=response_data)


class TokenIsNotValidAPIException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'token_error'
    default_detail = _('Token is not valid')


class TokenExpiredAPIException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'token_error'
    default_detail = _('Token expired')


class UserDoesNotExistAPIException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'user'
    default_detail = _('User does not exist')


class NotValidOTPAPIException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'otp'
    default_detail = _('OTP is not valid')


class IncorrectUsernamePasswordException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'login'
    default_detail = _("Email/Mobile or password is incorrect")
