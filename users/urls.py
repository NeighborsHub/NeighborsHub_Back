from django.urls import path

from users.views import RegisterAPI, VerifyEmailAPI

urlpatterns = [
    path('auth/register', RegisterAPI.as_view(), name='user_register'),
    path('auth/verify-email/<str:token>', VerifyEmailAPI.as_view(), name='user_verify_email')
]
