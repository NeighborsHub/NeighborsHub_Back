from django.urls import path

from users.views import PreRegisterAPI, VerifyPreRegisterAPI, RegisterAPI, VerifyEmailAPI, LoginApi, \
    SendVerifyMobileAPI, SendVerifyEmailAPI, LogoutApi, \
    VerifyMobileApi, SendOtpLoginApi, VerifyOtpLoginApi, SendForgetPasswordApi, VerifyOtpForgetPasswordApi, \
    VerifyEmailForgetPasswordAPI, VerifyOTPEmailAPI, ListCreateUserAddressAPI, RetrieveUpdateUserAddressAPI, \
    UpdateUserPasswordAPI, RequestSendOTPUpdateMobile, VerifySendOTPUpdateMobile, UnfollowUserAPI, FollowUserApi, \
    GoogleLoginAPI

urlpatterns = [
    path('auth/pre-register', PreRegisterAPI.as_view(), name='user_preregister'),
    path('auth/verify-pre-register', VerifyPreRegisterAPI.as_view(), name='user_verify_preregister'),
    path('auth/register', RegisterAPI.as_view(), name='user_register'),
    path('auth/verify-email/<str:token>', VerifyEmailAPI.as_view(), name='user_verify_email'),
    path('auth/login', LoginApi.as_view(), name='user_login'),
    path('auth/login/google', GoogleLoginAPI.as_view(), name='user_login_google'),
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
    path('me/address', ListCreateUserAddressAPI.as_view(), name='user_list_create_address'),
    path('me/address/<int:pk>', RetrieveUpdateUserAddressAPI.as_view(), name='user_get_update_address'),
    path('me/update-password', UpdateUserPasswordAPI.as_view(), name='user_update_password'),
    path('me/update-mobile', RequestSendOTPUpdateMobile.as_view(), name='user_update_mobile'),
    path('me/verify-update-mobile', VerifySendOTPUpdateMobile.as_view(), name='user_verify_update_mobile'),
    path('<int:user_pk>/follow', FollowUserApi.as_view(), name='user_follow'),
    path('<int:user_pk>/unfollow', UnfollowUserAPI.as_view(), name='user_unfollow'),

]
