import datetime
from rest_framework import status

from NeighborsHub.custom_jwt import generate_email_token, verify_custom_token, generate_auth_token
from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin
from rest_framework import generics
from django.utils.translation import gettext as _
from NeighborsHub.mail import SendEmail
from NeighborsHub.redis_management import VerificationEmailRedis, VerificationOTPRedis, AuthenticationTokenRedis
from NeighborsHub.utils import create_mobile_otp
from users.models import CustomerUser
from users.serializers import UserRegistrationSerializer, LoginSerializer
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
        otp = create_mobile_otp(length=5)
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


class LoginApi(APIView):
    @staticmethod
    def post(request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = get_user_model().objects.get_user_with_mobile_or_mail(
                    user_field=serializer.validated_data['email_mobile']
                )
                if not user.check_password(serializer.validated_data['password']):
                    return Response({"error": _("Email/Mobile or password is incorrect")},
                                    status=status.HTTP_400_BAD_REQUEST)
                # create jwt
                jwt = generate_auth_token(issued_for="Authorization", user_id=user.id)

                # save token in redis
                AuthenticationTokenRedis().create(jwt, user.id)

                return Response(data={"status": "ok", "data": {"access_token": f"Bearer {jwt}"}})
            except CustomerUser.DoesNotExist:
                return Response({"error": _("Email/Mobile or password is incorrect")},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
