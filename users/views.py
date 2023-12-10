import datetime
from rest_framework import status

from NeighborsHub.custom_jwt import generate_email_token, verify_custom_token
from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin
from rest_framework import generics
from django.utils.translation import gettext as _
from NeighborsHub.mail import SendEmail
from NeighborsHub.redis_management import VerificationEmailRedis, VerificationOTPRedis
from NeighborsHub.utils import create_mobile_otp
from users.models import CustomerUser
from users.serializers import UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model


class RegisterAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    singular_name = 'user'
    serializer_class = UserRegistrationSerializer

    @staticmethod
    def send_verification_email(user: CustomerUser) -> None:
        token = generate_email_token('Verify/Email', user.id,
                                     user.email,
                                     expired_at=datetime.datetime.now() + datetime.timedelta(days=1))
        redis = VerificationEmailRedis(issued_for='Verify/Email')
        redis.create(user.email, token)
        mail_sender = SendEmail()
        mail_sender.run(mail_destination=user.email, title=_('Verify Email'), body=token)
        return None

    @staticmethod
    def send_verification_mobile(user: CustomerUser) -> None:
        otp = create_mobile_otp(5)
        redis = VerificationOTPRedis(issued_for='Verify/Mobile')
        redis.create(user.mobile, otp)
        return None

    def perform_create(self, serializer):
        user = serializer.save()
        if user.email is not None:
            self.send_verification_email(user)
        if user.mobile is not None:
            self.send_verification_mobile(user)

        return user


class VerifyEmailAPI(APIView):

    @staticmethod
    def _is_exist_token_in_redis(email):
        redis_res = VerificationEmailRedis(issued_for='Verify/Email')
        return redis_res.get(keyword=email) is not None

    def get(self, request, token):
        has_error, token_payload = verify_custom_token(token)
        if has_error:
            return Response(token_payload, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_user_model().objects.get(id=token_payload['payload']['user_id'])
        except CustomerUser.DoesNotExist:
            return Response({"error": _("Token is not Valid.")}, status=status.HTTP_400_BAD_REQUEST)

        if user.email != token_payload['payload']['email']:
            return Response({"error": _("Token is not Valid.")}, status=status.HTTP_400_BAD_REQUEST)

        if not self._is_exist_token_in_redis(user.email):
            return Response({"error": _("Token is not Valid.")}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified_email = True
        user.verified_email_at = datetime.datetime.now()
        user.save()
        return Response({'status': 'ok'})


