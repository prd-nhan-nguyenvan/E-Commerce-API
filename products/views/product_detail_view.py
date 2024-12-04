from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.models import Product
from products.serializers import ProductSerializer
from products.tasks import delete_product_from_es, index_product_task
from products.utils import invalidate_product_cache


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
        """Retrieve product details."""
        return super().retrieve(request, *args, **kwargs)

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
        """Update product details."""
        product = self.get_object()
        data = request.data

        if "price" in data and float(data["price"]) < 0:
            return Response(
                {"error": "Price cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "sell_price" in data and float(data["sell_price"]) > float(
            data.get("price", product.price)
        ):
            return Response(
                {"error": "Sell price cannot be greater than the regular price."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = super().update(request, *args, **kwargs)

        invalidate_product_cache()

        index_product_task.delay(product.id)

        return Response(response.data, status=status.HTTP_200_OK)

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
        """Partially update product details."""
        response = super().partial_update(request, *args, **kwargs)

        invalidate_product_cache()

        product_id = kwargs["pk"]
        index_product_task.delay(product_id)

        return Response(response.data, status=status.HTTP_200_OK)

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
        product = self.get_object()
        super().destroy(request, *args, **kwargs)

        invalidate_product_cache()

        delete_product_from_es.delay(product.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
