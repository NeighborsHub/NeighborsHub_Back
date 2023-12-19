from rest_framework import serializers
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework_gis.serializers import GeoModelSerializer

from core.serializers import CitySerializer
from users.models import validate_email, validate_mobile, Address
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    email_mobile = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)
    otp = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'mobile', 'first_name', 'last_name', 'password', 'otp', 'email_mobile']

    @staticmethod
    def validate_email_mobile(value):
        if validate_email(value):
            if get_user_model().objects.filter(email=value.lower()).exists():
                raise serializers.ValidationError(_('Email registered before'))
            return value.lower()
        if validate_mobile(value):
            if get_user_model().objects.filter(mobile=value.lower()).exists():
                raise serializers.ValidationError(_('Mobile registered before'))
            return value.lower()
        raise serializers.ValidationError(_('Invalid email/mobile format'))

    def create(self, validated_data):
        is_email = validate_email(validated_data['email_mobile'])
        user = get_user_model().objects.create(
            email=validated_data['email_mobile'] if is_email else None,
            mobile=validated_data['email_mobile'] if not is_email else None,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            is_active=False,
            is_verified_mobile=False,
            is_verified_email=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    email_mobile = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_email_mobile(value):
        if validate_email(value):
            return value
        if validate_mobile(value):
            return value
        raise serializers.ValidationError(_('Invalid email/mobile format'))

    class Meta:
        model = get_user_model()
        fields = ['email_mobile', 'password']


class SendMobileOtpSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_mobile(value):
        if validate_mobile(value):
            return value
        raise serializers.ValidationError(_('Invalid mobile format'))

    class Meta:
        model = get_user_model()
        fields = ['mobile', ]


class VerifyOtpMobileSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(required=True, write_only=True)
    mobile = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_mobile(value):
        if validate_mobile(value):
            return value
        raise serializers.ValidationError(_('Invalid mobile format'))

    def validate_otp(self, value):
        # Perform validation logic here
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be an String.")
        mobile_regex = r"^[0-9]{5,}$"
        if re.match(mobile_regex, value) is not None:
            return value
        raise serializers.ValidationError(_('Invalid OTP format'))

    class Meta:
        model = get_user_model()
        fields = ['otp', 'mobile', ]


class SendEmailOtpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_email(value):
        if validate_email(value):
            return value.lower()
        raise serializers.ValidationError(_('Invalid email format'))

    class Meta:
        model = get_user_model()
        fields = ['email', ]


class VerifyEmailOtpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True, write_only=True)
    otp = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_email(value):
        if validate_email(value):
            return value.lower()
        raise serializers.ValidationError(_('Invalid email format'))

    def validate_otp(self, value):
        # Perform validation logic here
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be an String.")
        mobile_regex = r"^[0-9]{5,}$"
        if re.match(mobile_regex, value) is not None:
            return value
        raise serializers.ValidationError(_('Invalid OTP format'))

    class Meta:
        model = get_user_model()
        fields = ['email', 'otp']


class EmailMobileFieldSerializer(serializers.ModelSerializer):
    email_mobile = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_email_mobile(value):
        if validate_email(value):
            return value.lower()
        if validate_mobile(value):
            return value
        raise serializers.ValidationError(_('Invalid email/mobile format'))

    class Meta:
        model = get_user_model()
        fields = ['email_mobile', ]


class VerifyEmailMobileFieldSerializer(EmailMobileFieldSerializer):
    email_mobile = serializers.CharField(required=True, write_only=True)
    otp = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_email_mobile(value):
        if validate_email(value):
            return value.lower()
        if validate_mobile(value):
            return value
        raise serializers.ValidationError(_('Invalid email/mobile format'))

    def validate_otp(self, value):
        # Perform validation logic here
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be an String.")
        mobile_regex = r"^[0-9]{5,}$"
        if re.match(mobile_regex, value) is not None:
            return value
        raise serializers.ValidationError(_('Invalid OTP format'))

    class Meta:
        model = get_user_model()
        fields = ['email_mobile', 'otp', ]


class VerifyEmailForgetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['password', ]


class VerifyOtpForgetPasswordSerializer(VerifyOtpMobileSerializer, VerifyEmailForgetPasswordSerializer):
    class Meta:
        model = get_user_model()
        fields = ['otp', 'mobile', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'mobile', 'id']


class ListCreateAddressSerializer(GeoModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    street = serializers.CharField(required=False, max_length=255)
    city = CitySerializer(many=False, read_only=True)
    city_id = serializers.IntegerField(required=False, write_only=True)
    zip_code = serializers.CharField(required=False)
    is_main_address = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Address
        geometry_field = "location"
        fields = ['user', 'city', 'id', 'street', 'zip_code', 'is_main_address', 'city_id', 'user_id', 'location']