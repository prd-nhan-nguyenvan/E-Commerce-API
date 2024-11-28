from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.helpers import invalidate_product_cache
from products.models import Product
from products.serializers import ProductSerializer
from products.tasks import delete_product_from_es, index_product_task


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(tags=["Products"])
    def get(self, request, *args, **kwargs):
        """Retrieve product details."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Products"])
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

    @swagger_auto_schema(tags=["Products"])
    def patch(self, request, *args, **kwargs):
        """Partially update product details."""
        response = super().partial_update(request, *args, **kwargs)

        invalidate_product_cache()

        product_id = kwargs["pk"]
        index_product_task.delay(product_id)

        return Response(response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Products"])
    def delete(self, request, *args, **kwargs):
        """Delete a product."""
        product = self.get_object()
        super().destroy(request, *args, **kwargs)

        invalidate_product_cache()

        delete_product_from_es.delay(product.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
