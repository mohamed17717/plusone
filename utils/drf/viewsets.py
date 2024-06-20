from rest_framework import viewsets, mixins


# class CRUDLViewSet(
#         mixins.CreateModelMixin,
#         mixins.RetrieveModelMixin,
#         mixins.UpdateModelMixin,
#         mixins.DestroyModelMixin,
#         mixins.ListModelMixin,
#         viewsets.GenericViewSet):
#     pass


class RetrieveUpdateViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    pass
