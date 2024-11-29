from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.serializers import CategorySerializer
from products.services.category.CategoryService import CategoryService


class CategoryViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(tags=["Categories"])
    def list(self, request, *args, **kwargs):
        data = CategoryService.get_cached_category_list(request)
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={201: CategorySerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        CategoryService.invalidate_category_cache()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
