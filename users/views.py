import datetime
from rest_framework import status

from NeighborsHub.custom_jwt import verify_custom_token, generate_auth_token
from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin, \
    ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin
from rest_framework import generics
from django.utils.translation import gettext as _

from NeighborsHub.exceptions import TokenIsNotValidAPIException, UserDoesNotExistAPIException, NotValidOTPAPIException, \
    IncorrectUsernamePasswordException, ObjectNotFoundException
from NeighborsHub.permission import CustomAuthentication, IsOwnerAuthentication
from NeighborsHub.redis_management import VerificationEmailRedis, VerificationOTPRedis, AuthenticationTokenRedis
from users.models import CustomerUser, validate_email, Address
from users.serializers import UserRegistrationSerializer, LoginSerializer, \
    SendMobileOtpSerializer, VerifyOtpMobileSerializer, EmailMobileFieldSerializer, VerifyOtpForgetPasswordSerializer, \
    VerifyEmailForgetPasswordSerializer, SendEmailOtpSerializer, VerifyEmailOtpSerializer, \
    VerifyEmailMobileFieldSerializer, ListCreateAddressSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from users.utils import send_otp_mobile, send_token_email, send_otp_email


class PreRegisterAPI(APIView):
    @staticmethod
    def post(request):
        serializer = EmailMobileFieldSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            is_email = validate_email(serializer.validated_data['email_mobile'])
            try:
                get_user_model().objects.get_user_with_mobile_or_mail(
                    user_field=serializer.validated_data['email_mobile'])
                response_data = {'status': "error", 'data': '', 'message': _('User registered before')}
                return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
            except CustomerUser.DoesNotExist:
                pass
            if is_email:
                send_otp_email(serializer.validated_data['email_mobile'], issued_for="Verify/Email")
                response_message = _('Email sent')
            else:
                send_otp_mobile(serializer.validated_data['email_mobile'], issued_for="Verify/Mobile")
                response_message = _('SMS sent')
            response_data = {'status': "ok", 'data': '', 'message': response_message}
            return Response(data=response_data, status=status.HTTP_200_OK)


class VerifyPreRegisterAPI(APIView):
    @staticmethod
    def is_valid_otp(otp: str, email_mobile: str) -> bool:
        issued_for = "Verify/Email" if validate_email(email_mobile) else "Verify/Mobile"
        redis_manager = VerificationOTPRedis(issued_for=issued_for)
        redis_otp = redis_manager.get(email_mobile)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return otp == redis_otp

    @staticmethod
    def is_user_exist(email_mobile):
        try:
            get_user_model().objects.get_user_with_mobile_or_mail(user_field=email_mobile)
            return True
        except CustomerUser.DoesNotExist:
            return False

    def post(self, request):
        serializer = VerifyEmailMobileFieldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.is_user_exist(serializer.validated_data['email_mobile']):
            response_data = {'status': "error", 'data': '', 'message': _('User registered before')}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
        if not self.is_valid_otp(serializer.validated_data['otp'], serializer.validated_data['email_mobile']):
            response_data = {'status': "error", 'data': {'otp': [_('OTP is not valid')]},
                             'message': 'Invalid Input'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"status": "ok", "message": _('OTP is valid')}, status=status.HTTP_200_OK)


class RegisterAPI(ExpressiveCreateModelMixin, generics.CreateAPIView, VerifyPreRegisterAPI):
    singular_name = 'user'
    serializer_class = UserRegistrationSerializer

    @staticmethod
    def create_jwt_authorization(user_id):
        # create jwt
        jwt = generate_auth_token(issued_for="Authorization", user_id=user_id)
        # save token in redis
        AuthenticationTokenRedis().create(jwt, user_id)
        return jwt

    def perform_create(self, serializer):
        user = serializer.save()
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.is_valid_otp(serializer.validated_data['otp'], serializer.validated_data['email_mobile']):
            response_data = {'status': "error", 'data': {'otp': [_('OTP is not valid')]},
                             'message': 'Invalid Input'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        user = self.perform_create(serializer)
        response_data = {
            'status': "ok",
            'data': {"user": serializer.data, "access_token": f"Bearer {self.create_jwt_authorization(user.id)}"},
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class VerifyEmailAPI(APIView):

    @staticmethod
    def _is_exist_token_in_redis(email):
        redis_res = VerificationEmailRedis(issued_for='Verify/Email')
        return redis_res.get(keyword=email) is not None

    def get(self, request, token):
        has_error, token_payload = verify_custom_token(token)
        try:
            user = get_user_model().objects.get(id=token_payload['payload']['user_id'])
        except CustomerUser.DoesNotExist:
            raise TokenIsNotValidAPIException

        if user.email != token_payload['payload']['email'] or not self._is_exist_token_in_redis(user.email):
            raise TokenIsNotValidAPIException

        user.is_verified_email = True
        user.verified_email_at = datetime.datetime.now()
        user.save()
        return Response({'status': 'ok'})


class LoginApi(APIView):
    @staticmethod
    def post(request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = get_user_model().objects.get_user_with_mobile_or_mail(
                    user_field=serializer.validated_data['email_mobile']
                )
                if not user.check_password(serializer.validated_data['password']):
                    raise IncorrectUsernamePasswordException

                # create jwt
                jwt = generate_auth_token(issued_for="Authorization", user_id=user.id)

                # save token in redis
                AuthenticationTokenRedis().create(jwt, user.id)

                return Response(data={"status": "ok", "data": {"access_token": f"Bearer {jwt}"}})
            except CustomerUser.DoesNotExist:
                raise IncorrectUsernamePasswordException

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOtpLoginApi(APIView):

    @staticmethod
    def post(request):
        serializer = SendMobileOtpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = get_user_model().objects.get(
                    mobile=serializer.validated_data['mobile']
                )
                send_otp_mobile(user.mobile, issued_for='OTP/Login')
                return Response(data={"status": "ok", "data": {}, "message": _('OTP send successfully')})
            except CustomerUser.DoesNotExist:
                raise UserDoesNotExistAPIException

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpLoginApi(APIView):
    @staticmethod
    def get_verification_redis_mobile_otp(user: CustomerUser) -> str:
        redis = VerificationOTPRedis(issued_for='OTP/Login')
        redis_otp = redis.get(user.mobile)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return redis_otp

    def post(self, request):
        serializer = VerifyOtpMobileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = get_user_model().objects.get(
                    mobile=serializer.validated_data['mobile']
                )
                redis_otp = self.get_verification_redis_mobile_otp(user)
                if redis_otp is None or redis_otp != serializer.validated_data['otp']:
                    raise NotValidOTPAPIException
                jwt = generate_auth_token(issued_for="Authorization", user_id=user.id)
                # save token in redis
                AuthenticationTokenRedis().create(jwt, user.id)
                return Response(data={"status": "ok", "data": {"access_token": f"Bearer {jwt}"}})
            except CustomerUser.DoesNotExist:
                raise UserDoesNotExistAPIException
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerifyMobileAPI(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def post(request):
        serializer = SendMobileOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if get_user_model().objects.filter(mobile=serializer.validated_data['mobile']).exists():
            response_data = {'status': "error", 'data': '', 'message': _('Mobile exist')}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
        send_otp_mobile(serializer.validated_data['mobile'], issued_for="Verify/Mobile")
        response_message = _('SMS sent')
        response_data = {'status': "ok", 'data': '', 'message': response_message}
        return Response(data=response_data, status=status.HTTP_200_OK)


class VerifyMobileApi(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def is_valid_otp(otp, mobile: str) -> bool:
        redis = VerificationOTPRedis(issued_for='Verify/Mobile')
        redis_otp = redis.get(mobile)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return redis_otp == otp

    def post(self, request):
        serializer = VerifyOtpMobileSerializer(data=request.data)
        user = request.user
        serializer.is_valid(raise_exception=True)
        if get_user_model().objects.filter(mobile=serializer.validated_data['mobile']).exists():
            response_data = {'status': "error", 'data': '', 'message': _('Mobile exist')}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
        if not self.is_valid_otp(serializer.validated_data['otp'], serializer.validated_data['mobile']):
            raise NotValidOTPAPIException
        user.mobile = serializer.validated_data['mobile']
        user.is_verified_mobile = True
        user.verified_mobile_at = datetime.datetime.now()
        user.save()
        return Response(data={"status": "ok", "data": {}, 'message': _('Mobile Saved')})


class VerifyOTPEmailAPI(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def is_valid_otp(otp, email: str) -> bool:
        redis = VerificationOTPRedis(issued_for='Verify/Email')
        redis_otp = redis.get(email)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return redis_otp == otp

    def post(self, request):
        serializer = VerifyEmailOtpSerializer(data=request.data)
        user = request.user
        serializer.is_valid(raise_exception=True)
        if get_user_model().objects.filter(email=serializer.validated_data['email']).exists():
            response_data = {'status': "error", 'data': '', 'message': _('Email exists')}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
        if not self.is_valid_otp(serializer.validated_data['otp'], serializer.validated_data['email']):
            raise NotValidOTPAPIException
        user.email = serializer.validated_data['email']
        user.is_verified_email = True
        user.verified_email_at = datetime.datetime.now()
        user.save()
        return Response(data={"status": "ok", "data": {}, 'message': _('Email Saved')})


class SendVerifyEmailAPI(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def post(request):
        serializer = SendEmailOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if get_user_model().objects.filter(email=serializer.validated_data['email']).exists():
            response_data = {'status': "error", 'data': '', 'message': _('Email exists')}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
        send_otp_email(serializer.validated_data['email'], issued_for="Verify/Email")
        response_message = _('Email sent')
        response_data = {'status': "ok", 'data': '', 'message': response_message}
        return Response(data=response_data, status=status.HTTP_200_OK)


class LogoutApi(APIView):
    authentication_classes = (CustomAuthentication,)

    @staticmethod
    def get(request):
        redis_manager = AuthenticationTokenRedis()
        token = request.META.get('HTTP_AUTHORIZATION')
        token = token.split()[1]
        redis_manager.revoke(token)
        return Response(data={"status": "ok", "data": {}, "message": _("Logout successfully")})


class SendForgetPasswordApi(APIView):

    @staticmethod
    def get_verification_redis_mobile_otp(user: CustomerUser) -> str:
        redis = VerificationOTPRedis(issued_for='Verify/Mobile')
        redis_otp = redis.get(user.mobile)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return redis_otp

    def post(self, request):
        serializer = EmailMobileFieldSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = get_user_model().objects.get_user_with_mobile_or_mail(
                    user_field=serializer.validated_data['email_mobile']
                )
                if serializer.validated_data['email_mobile'] == user.email:
                    token = send_token_email(user, issued_for="ForgetPassword/Email")
                    return Response(data={"status": "ok", "message": _("Email Sent"), "verify_email_token": token})

                send_otp_mobile(mobile=user.mobile, issued_for="ForgetPassword/OTP")
                return Response(data={"status": "ok", "message": _("OTP Sent")})
            except CustomerUser.DoesNotExist:
                raise UserDoesNotExistAPIException
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpForgetPasswordApi(APIView):
    @staticmethod
    def get_verification_redis_mobile_otp(user: CustomerUser) -> str:
        redis = VerificationOTPRedis(issued_for='ForgetPassword/OTP')
        redis_otp = redis.get(user.mobile)
        if isinstance(redis_otp, bytes):
            redis_otp = redis_otp.decode('utf-8')
        return redis_otp

    def post(self, request):
        serializer = VerifyOtpForgetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = get_user_model().objects.get(mobile=serializer.validated_data['mobile'])
                redis_otp = self.get_verification_redis_mobile_otp(user)
                if redis_otp is None or redis_otp != serializer.validated_data['otp']:
                    raise NotValidOTPAPIException
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response(data={"status": "ok", "message": _('Password Changed')})
            except CustomerUser.DoesNotExist:
                raise UserDoesNotExistAPIException

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailForgetPasswordAPI(APIView):
    @staticmethod
    def _is_exist_token_in_redis(email):
        redis_res = VerificationEmailRedis(issued_for='ForgetPassword/Email')
        return redis_res.get(keyword=email) is not None

    def check_token(self, token):
        has_error, token_payload = verify_custom_token(token)
        try:
            user = get_user_model().objects.get(id=token_payload['payload']['user_id'])
        except CustomerUser.DoesNotExist:
            raise TokenIsNotValidAPIException
        if user.email != token_payload['payload']['email'] or not self._is_exist_token_in_redis(user.email):
            raise TokenIsNotValidAPIException
        return user

    def get(self, request, token):
        user = self.check_token(token)
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return Response({'status': 'ok', 'data': {"user": user_data}})

    def post(self, request, token):
        user = self.check_token(token)
        serializer = VerifyEmailForgetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(data={"status": "ok", "message": _('Password Changed')})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCreateUserAddressAPI(ExpressiveCreateModelMixin, ExpressiveListModelMixin, generics.ListCreateAPIView):
    authentication_classes = (CustomAuthentication,)
    serializer_class = ListCreateAddressSerializer
    queryset = Address.objects.filter()
    singular_name = 'address'
    plural_name = 'addresses'

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user, city_id=serializer.validated_data['city_id'])
        return address

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class RetrieveUpdateUserAddressAPI(ExpressiveUpdateModelMixin, ExpressiveRetrieveModelMixin,
                                   generics.RetrieveUpdateAPIView):
    authentication_classes = (CustomAuthentication, )
    permission_classes = (IsOwnerAuthentication, )
    serializer_class = ListCreateAddressSerializer
    queryset = Address.objects.filter()
    singular_name = 'address'

    def get_object(self):
        try:
            obj = Address.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
        except Address.DoesNotExist:
            raise ObjectNotFoundException
        return obj
