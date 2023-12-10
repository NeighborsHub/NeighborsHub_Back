from rest_framework.mixins import CreateModelMixin, UpdateModelMixin


class ExpressiveListModelMixin:

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self, 'sort_fields') and len(self.sort_fields) != 0:
            if self.request.GET.get('order_by', None) and self.request.GET.get('order_by', None) in self.sort_fields:
                return qs.order_by(*self.sort_fields)
            else:
                return qs
        else:
            return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {'status': 'ok', 'data': {self.plural_name: response.data}}
        return response


class ExpressiveRetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = {'status': 'ok', 'data': {self.singular_name: response.data}}
        return response


class ExpressiveCreateModelMixin(CreateModelMixin):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {'status': 'ok', 'data': {self.singular_name: response.data}}
        return response


class ExpressiveUpdateModelMixin(UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {'status': 'ok', 'data': {self.singular_name: response.data}}
        return response
