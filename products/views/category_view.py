from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.serializers import CategorySerializer
from products.serializers.category_serializers import PaginatedCategorySerializer
from products.services.category.CategoryService import CategoryService


class CategoryViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(
        tags=["Categories"],
        operation_summary="Retrieve all categories",
        operation_description="Returns a paginated list of all categories available in the system.",
        responses={
            status.HTTP_200_OK: PaginatedCategorySerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid request parameters"
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Number of items to retrieve per page",
                type=openapi.TYPE_INTEGER,
                default=10,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Starting position of items to retrieve",
                type=openapi.TYPE_INTEGER,
                default=0,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        data = CategoryService.get_cached_category_list(request)
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_summary="Create a new category",
        operation_description="Allows admin or staff to create a new category.",
        request_body=CategorySerializer,
        responses={
            status.HTTP_201_CREATED: CategorySerializer,
            status.HTTP_400_BAD_REQUEST: "Invalid data",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        CategoryService.invalidate_category_cache()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_summary="Retrieve a specific category",
        operation_description="Fetch details of a category by its primary key (id).",
        responses={
            status.HTTP_200_OK: CategorySerializer,
            status.HTTP_404_NOT_FOUND: "Category not found.",
        },
    )
    def retrieve(self, request, pk=None):
        category = CategoryService.get_category(pk)
        if not category:
            return Response(
                {"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(CategorySerializer(category).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_summary="Fully update a category",
        operation_description="Fully update an existing category using its primary key (PUT).",
        request_body=CategorySerializer,
        responses={
            status.HTTP_200_OK: CategorySerializer,
            status.HTTP_404_NOT_FOUND: "Category not found.",
        },
    )
    def update(self, request, pk=None):
        category = CategoryService.get_category(pk)
        if not category:
            return Response(
                {"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategorySerializer(
            category, data=request.data, partial=False, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_category = serializer.save()
        CategoryService.invalidate_category_cache()
        response_data = CategorySerializer(updated_category).data

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_summary="Partially update a category",
        operation_description="Partially update an existing category using its primary key (PATCH).",
        request_body=CategorySerializer,
        responses={
            status.HTTP_200_OK: CategorySerializer,
            status.HTTP_404_NOT_FOUND: "Category not found.",
        },
    )
    def partial_update(self, request, pk=None):
        category = CategoryService.get_category(pk)
        if not category:
            return Response(
                {"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategorySerializer(
            category, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_category = serializer.save()
        CategoryService.invalidate_category_cache()
        response_data = CategorySerializer(updated_category).data

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_summary="Delete a category",
        operation_description="Delete a category by its primary key (id).",
        responses={
            status.HTTP_204_NO_CONTENT: "No content",
            status.HTTP_404_NOT_FOUND: "Category not found.",
        },
    )
    def destroy(self, request, pk=None):
        category = CategoryService.get_category(pk)
        if not category:
            return Response(
                {"detail": "Category not found."},
                status=status.HTTP_status.HTTP_404_NOT_FOUND_NOT_FOUND,
            )
        category.delete()
        CategoryService.invalidate_category_cache()
        return Response(status=status.HTTP_204_NO_CONTENT)
