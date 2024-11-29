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

    @swagger_auto_schema(tags=["Categories"])
    def retrieve(self, request, pk=None):
        category = CategoryService.get_category(pk)
        return Response(CategorySerializer(category).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Categories"])
    def update(self, request, pk=None):
        category = CategoryService.get_category(pk)
        if not category:
            return Response(
                {"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Deserialize and validate the request data
        serializer = CategorySerializer(
            category, data=request.data, partial=False, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Save the updated instance
        updated_category = serializer.save()  # This returns the model instance

        # Invalidate the cache for consistency
        CategoryService.invalidate_category_cache()

        # Serialize the updated instance to send as a response
        response_data = CategorySerializer(updated_category).data

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Categories"])
    def destroy(self, request, pk=None):
        category = CategoryService.get_category(pk)
        category.delete()
        CategoryService.invalidate_category_cache()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(tags=["Categories"])
    def put(self, request, pk=None):
        return self.update(request, pk)

    @swagger_auto_schema(tags=["Categories"])
    def patch(self, request, pk=None):
        return self.update(request, pk)
