from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.serializers import ProductSerializer
from products.services.product.ProductService import ProductService
from products.tasks import index_product_task
from products.utils import invalidate_product_cache


class ProductViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(
        tags=["Products"],
        operation_summary="List products",
        operation_description=(
            "Retrieve a paginated list of products with filtering, ordering, and search capabilities."
        ),
        manual_parameters=[
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("offset", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("category", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("price", openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
            openapi.Parameter("name", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(
                "description", openapi.IN_QUERY, type=openapi.TYPE_STRING
            ),
        ],
        responses={200: ProductSerializer(many=True)},
    )
    def list(self, request):
        """
        List products with optional filtering and pagination.
        """

        data = ProductService.get_filtered_products(request)
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Products"],
        operation_summary="Create a product",
        operation_description="Create a new product in the system.",
        request_body=ProductSerializer,
        responses={201: ProductSerializer, 400: "Validation Error"},
    )
    def create(self, request):
        """
        Create a new product.
        """
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService.create_product(serializer.validated_data)

        # Trigger background tasks
        index_product_task.delay(product.id)
        invalidate_product_cache()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
