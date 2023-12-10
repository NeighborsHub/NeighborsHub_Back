from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin
from rest_framework import generics

from users.serializers import UserRegistrationSerializer


class RegisterAPI(ExpressiveCreateModelMixin, generics.CreateAPIView):
    singular_name = 'user'
    serializer_class = UserRegistrationSerializer
