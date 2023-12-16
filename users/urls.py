from django.urls import path

from users.views import PreRegisterAPI, VerifyPreRegisterAPI, RegisterAPI, VerifyEmailAPI, LoginApi, \
    SendVerifyMobileAPI, SendVerifyEmailAPI, LogoutApi, \
    VerifyMobileApi, SendOtpLoginApi, VerifyOtpLoginApi, SendForgetPasswordApi, VerifyOtpForgetPasswordApi, \
    VerifyEmailForgetPasswordAPI, VerifyOTPEmailAPI

urlpatterns = [
    path('auth/pre-register', PreRegisterAPI.as_view(), name='user_preregister'),
    path('auth/verify-pre-register', VerifyPreRegisterAPI.as_view(), name='user_verify_preregister'),
    path('auth/register', RegisterAPI.as_view(), name='user_register'),
    path('auth/verify-email/<str:token>', VerifyEmailAPI.as_view(), name='user_verify_email'),
    path('auth/login', LoginApi.as_view(), name='user_login'),
    path('auth/send-otp-login', SendOtpLoginApi.as_view(), name='user_send_otp_login'),
    path('auth/verify-otp-login', VerifyOtpLoginApi.as_view(), name='user_verify_otp_login'),
    path('auth/verify-mobile', VerifyMobileApi.as_view(), name='user_verify_mobile'),
    path('auth/send-verify-mobile', SendVerifyMobileAPI.as_view(), name='user_send_verify_mobile'),
    path('auth/send-verify-email', SendVerifyEmailAPI.as_view(), name='user_send_verify_otp_email'),
    path('auth/verify-email', VerifyOTPEmailAPI.as_view(), name='user_verify_otp_email'),
    path('auth/logout', LogoutApi.as_view(), name='user_logout'),
    path('auth/send-forget-password', SendForgetPasswordApi.as_view(), name='send_forget_password'),
    path('auth/verify-otp-forget-password', VerifyOtpForgetPasswordApi.as_view(),
         name='verify_otp_forget_password'),
    path('auth/verify-email-forget-password/<str:token>', VerifyEmailForgetPasswordAPI.as_view(),
         name='verify_email_forget_password'),

]
