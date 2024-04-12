from rest_framework import serializers
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework_gis.serializers import GeoModelSerializer

from albums.serializers import UserAvatarSerializer
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
    email = serializers.SerializerMethodField('get_user_public_email')
    mobile = serializers.SerializerMethodField('get_user_public_mobile')
    avatar = serializers.SerializerMethodField('get_last_user_avatar')
    follower_count = serializers.SerializerMethodField('get_user_follower_count')
    following_count = serializers.SerializerMethodField('get_user_following_count')
    posts_count = serializers.SerializerMethodField('get_user_posts_count')

    def get_user_public_email(self, obj):
        if obj.email is not None and self.context['request'].user is None:
            return f"{obj.email[:2]}***{obj.email[-5:]}"
        return obj.email

    def get_user_public_mobile(self, obj):
        if obj.mobile is not None and self.context['request'].user is None:
            return f"{obj.mobile[:3]}***{obj.mobile[-2:]}"
        return obj.mobile

    def get_user_follower_count(self, obj):
        return obj.following.count()

    def get_user_following_count(self, obj):
        return obj.follower.count()

    def get_user_posts_count(self, obj):
        return obj.posts_created_by.count()

    def get_last_user_avatar(self, obj):
        try:
            qs = obj.get_avatar()
            return UserAvatarSerializer(instance=qs, many=False, context=self.context).data
        except Exception:
            return None

    #
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'mobile', 'id', 'avatar', 'follower_count', 'following_count',
                  'posts_count']


class UserPublicSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField('get_user_public_email')
    mobile = serializers.SerializerMethodField('get_user_public_mobile')
    avatar = serializers.SerializerMethodField('get_last_user_avatar')

    def get_user_public_email(self, obj):
        if obj.email is not None and self.context['request'].user is None:
            return f"{obj.email[:2]}***{obj.email[-5:]}"
        return obj.email

    def get_user_public_mobile(self, obj):
        if obj.mobile is not None and self.context['request'].user is None:
            return f"{obj.mobile[:3]}***{obj.mobile[-2:]}"
        return obj.mobile

    def get_last_user_avatar(self, obj):
        qs = obj.avatar.last()
        return UserAvatarSerializer(instance=qs, many=False).data

    #
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'mobile', 'id', 'avatar']


class ListCreateAddressSerializer(GeoModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    street = serializers.CharField(required=False, max_length=255)
    city = CitySerializer(many=False, read_only=True)
    city_id = serializers.IntegerField(required=False, write_only=True)
    zip_code = serializers.CharField(required=False)
    is_main_address = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Address
        geo_field = "location"
        fields = ['user', 'city', 'id', 'street', 'zip_code', 'is_main_address', 'city_id', 'user_id', 'location']


class AddressSerializer(GeoModelSerializer):
    street = serializers.CharField(required=False, max_length=255)
    city = CitySerializer(many=False, read_only=True)
    zip_code = serializers.CharField(required=False)
    is_main_address = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Address
        geo_field = "location"
        fields = ['city', 'id', 'street', 'zip_code', 'is_main_address', 'location']


class UpdateUserPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password']


class UpdateMobileSerializer(serializers.ModelSerializer):
    new_mobile = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['new_mobile', ]


class VerifyUpdateMobileSerializer(serializers.ModelSerializer):
    new_mobile = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(required=True, write_only=True)
    otp = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['new_mobile', 'token', 'otp', ]


class GoogleOATHLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class GoogleSetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
