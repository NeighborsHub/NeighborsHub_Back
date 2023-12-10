from django.urls import path

from users.views import RegisterAPI

urlpatterns = [
    path('auth/register', RegisterAPI.as_view(), name='user_register'),
    path('auth/verify-email/<str:token>', RegisterAPI.as_view(), name='verify_email')
]
