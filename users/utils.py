from datetime import datetime, timedelta

from NeighborsHub.custom_jwt import generate_email_token
from NeighborsHub.mail import SendEmail
from NeighborsHub.redis_management import VerificationOTPRedis, VerificationEmailRedis
from NeighborsHub.sms import SendSMS
from NeighborsHub.utils import create_mobile_otp
from users.models import CustomerUser
from django.utils.translation import gettext as _


def send_otp_mobile(mobile: str, issued_for: str) -> None:
    otp = create_mobile_otp(length=5)
    otp = "12345"  # mock otp
    redis_manager = VerificationOTPRedis(issued_for=issued_for)
    redis_manager.revoke(mobile)
    redis_manager.create(mobile, otp)
    # TODO: USE issue_for message
    SendSMS().run(mobile=mobile, message=otp)
    return None


def send_token_email(user: CustomerUser, issued_for: str) -> None:
    token = generate_email_token(issued_for, user.id, user.email, expired_at=datetime.now() + timedelta(days=1))
    redis_manager = VerificationEmailRedis(issued_for=issued_for)
    redis_manager.revoke(user.email)
    redis_manager.create(user.email, token)

    mail_sender = SendEmail()
    # TODO: USE issue_for message body and title
    mail_sender.run(mail_destination=user.email, title=_(issued_for), body=token)
    return token


def send_otp_email(email: str, issued_for: str) -> None:
    otp = create_mobile_otp(length=5)
    otp = "12345"  # mock otp
    redis_manager = VerificationOTPRedis(issued_for=issued_for)
    redis_manager.revoke(email)
    redis_manager.create(email, otp)

    mail_sender = SendEmail()
    # TODO: USE issue_for message body and title
    mail_sender.run(mail_destination=email, title=_(issued_for), body=otp)
    return None
