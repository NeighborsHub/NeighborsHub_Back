from rest_framework import serializers
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

from users.models import validate_email, validate_mobile
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'mobile', 'first_name', 'last_name', 'password']

    def validate(self, values):
        email = values.get('email')
        mobile = values.get('mobile')

        if email is None and mobile is None:
            raise serializers.ValidationError(
                {'mobile_email_field_errors': [_('Ether Email or Mobile must be provided.')]})
        return values

    @staticmethod
    def validate_email(value):
        if value is not None:
            if not validate_email(value):
                raise serializers.ValidationError(_('Invalid email format'))
            if get_user_model().objects.filter(email=value).exists():
                raise serializers.ValidationError(_('Email is existed.'))
        return value

    @staticmethod
    def validate_mobile(value):
        if value is not None:
            if not validate_mobile(value):
                raise serializers.ValidationError(_('Invalid email format'))
            if get_user_model().objects.filter(mobile=value).exists():
                raise serializers.ValidationError(_('Mobile is existed.'))
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create(
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
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


class SendLoginOtpSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_email_mobile(value):
        if validate_mobile(value):
            return value
        raise serializers.ValidationError(_('Invalid mobile format'))

    class Meta:
        model = get_user_model()
        fields = ['mobile', ]


class VerifyMobileSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def validate_otp(value):
        mobile_regex = r"^[0-9]{5,}$"
        if re.match(mobile_regex, value) is not None:
            return value
        raise serializers.ValidationError(_('Invalid OTP format'))

    class Meta:
        model = get_user_model()
        fields = ['otp', ]
