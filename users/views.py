import datetime

from NeighborsHub.custom_jwt import generate_email_token
from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin
from rest_framework import generics
from django.utils.translation import gettext as _
from NeighborsHub.mail import SendEmail
from NeighborsHub.redis_management import VerificationEmailRedis, VerificationOTPRedis
from NeighborsHub.utils import create_mobile_otp
from users.models import CustomerUser
from users.serializers import UserRegistrationSerializer


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
