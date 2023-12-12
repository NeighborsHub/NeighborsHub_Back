import datetime
from rest_framework import status

from NeighborsHub.custom_jwt import verify_custom_token, generate_auth_token
from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin
from rest_framework import generics
from django.utils.translation import gettext as _
from NeighborsHub.permission import CustomAuthentication
from NeighborsHub.redis_management import VerificationEmailRedis, VerificationOTPRedis, AuthenticationTokenRedis
from users.models import CustomerUser
from users.serializers import UserRegistrationSerializer, LoginSerializer, VerifyMobileSerializer, \
    SendLoginOtpSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from users.utils import send_otp_mobile, send_token_email


class RegisterAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    singular_name = 'user'
    serializer_class = UserRegistrationSerializer

    @staticmethod
    def send_verify_email(user: CustomerUser) -> None:
        send_token_email(user, 'Verify/Email')
        return None

    @staticmethod
    def send_verification_mobile(user: CustomerUser) -> None:
        send_otp_mobile(user.mobile, issued_for="Verify/Mobile")
        return None

    @staticmethod
    def create_jwt_authorization(user_id):
        # create jwt
        jwt = generate_auth_token(issued_for="Authorization", user_id=user_id)
        # save token in redis
        AuthenticationTokenRedis().create(jwt, user_id)
        return jwt

    def perform_create(self, serializer):
        user = serializer.save()
        if user.email is not None:
            self.send_token_email(user)
        if user.mobile is not None:
            self.send_verification_mobile(user)
        # create jwt
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        response_data = {
            'status': "ok",
            'data': {"user": serializer.data, "access_token": f"Bearer {self.create_jwt_authorization(user.id)}"}
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


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


class SendOtpLoginApi(APIView):

    @staticmethod
    def post(request):
        serializer = SendLoginOtpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = get_user_model().objects.get(
                    mobile=serializer.validated_data['mobile']
                )
                send_otp_mobile(user.mobile, issued_for='OTP/Login')
                return Response(data={"status": "ok", "data": {}})
            except CustomerUser.DoesNotExist:
                return Response({"error": _("User does not exist")},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyMobileApi(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def get_verification_redis_mobile_otp(user: CustomerUser) -> str:
        redis = VerificationOTPRedis(issued_for='Verify/Mobile')
        redis_otp = redis.get(user.mobile)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return redis_otp

    def post(self, request):
        serializer = VerifyMobileSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            redis_otp = self.get_verification_redis_mobile_otp(user)
            if redis_otp is None or redis_otp != serializer.validated_data['otp']:
                return Response({"error": _("OTP is not valid")}, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified_mobile = True
            user.verified_mobile_at = datetime.datetime.now()
            user.save()
            return Response(data={"status": "ok", "data": {}})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerifyEmailApi(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def get(request):
        user = request.user
        send_token_email(user, 'Verify/Email')
        return Response(data={"status": "ok", "data": {}})


class ResendVerifyMobileApi(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def get(request):
        user = request.user
        send_otp_mobile(user.mobile, issued_for='Verify/Mobile')
        return Response(data={"status": "ok", "data": {}})


class LogoutApi(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def get(request):
        redis_manager = AuthenticationTokenRedis()
        token = request.META.get('HTTP_Authorization')
        token = token.split()[1]
        redis_manager.revoke(token)
        return Response(data={"status": "ok", "data": {}})
