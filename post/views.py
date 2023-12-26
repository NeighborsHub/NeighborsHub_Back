from rest_framework import generics

from NeighborsHub.custom_view_mixin import ExpressiveCreateModelMixin, ExpressiveListModelMixin
from NeighborsHub.permission import CustomAuthentication


class ListCreateUserPostAPI(ExpressiveCreateModelMixin, ExpressiveListModelMixin, generics.ListCreateAPIView):
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
