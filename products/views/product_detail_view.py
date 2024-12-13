from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.models import Product
from products.serializers import ProductSerializer
from products.services.product import ProductService


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(
        tags=["Products"],
        operation_summary="Retrieve product details",
        operation_description="Retrieve the details of a specific product by its ID.",
        responses={
            200: ProductSerializer,
            404: openapi.Response(description="Product not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        product = ProductService.get_product(kwargs.get("pk"))
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Products"],
        operation_summary="Update product details",
        operation_description=(
            "Update the details of a product. "
            "Includes validation for price and sell price."
        ),
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: openapi.Response(description="Validation error"),
        },
    )
    def put(self, request, *args, **kwargs):
        product = ProductService.get_product(kwargs.get("pk"))
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data, errors = ProductService.update_product(product, request.data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Products"],
        operation_summary="Partially update product details",
        operation_description="Update specific fields of a product.",
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: openapi.Response(description="Validation error"),
        },
    )
    def patch(self, request, *args, **kwargs):
        product = ProductService.get_product(kwargs.get("pk"))
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data, errors = ProductService.update_product(product, request.data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Products"],
        operation_summary="Delete a product",
        operation_description="Delete a product by its ID. This action is irreversible.",
        responses={
            204: openapi.Response(description="Product successfully deleted"),
            404: openapi.Response(description="Product not found"),
        },
    )
    def delete(self, request, *args, **kwargs):
        product = ProductService.get_product(kwargs.get("pk"))
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ProductService.delete_product(product)
        return Response(status=status.HTTP_204_NO_CONTENT)
