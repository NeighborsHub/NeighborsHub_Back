from django.urls import path

from users.views import RegisterAPI, VerifyEmailAPI, LoginApi, ResendVerifyMobileApi, ResendVerifyEmailApi, LogoutApi

urlpatterns = [
    path('auth/register', RegisterAPI.as_view(), name='user_register'),
    path('auth/verify-email/<str:token>', VerifyEmailAPI.as_view(), name='user_verify_email'),
    path('auth/login', LoginApi.as_view(), name='user_login'),
    path('auth/verify-mobile', LoginApi.as_view(), name='user_verify_mobile'),
    path('auth/resend-verify-mobile', ResendVerifyMobileApi.as_view(), name='user_resend_verify_mobile'),
    path('auth/resend-verify-email', ResendVerifyEmailApi.as_view(), name='user_resend_verify_mobile'),
    path('auth/logout', LogoutApi.as_view(), name='user_logout'),
]
