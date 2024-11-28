from django.conf import settings
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.models import Product
from products.serializers import ProductSerializer
from products.tasks import index_product_task
from products.utils import invalidate_product_cache


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").only(
        "id",
        "category",
        "name",
        "slug",
        "description",
        "price",
        "sell_price",
        "on_sell",
        "stock",
        "image",
        "created_at",
        "updated_at",
    )
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["category", "price"]
    ordering_fields = ["name", "price", "created_at"]
    search_fields = ["name", "description"]

    default_limit = getattr(settings, "DEFAULT_LIMIT", 10)
    default_offset = getattr(settings, "DEFAULT_OFFSET", 0)

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    def get_queryset(self):
        queryset = Product.objects.select_related("category").only(
            "id", "name", "description", "price", "created_at", "category_id"
        )

        category = self.request.query_params.get("category")
        price = self.request.query_params.get("price")
        name = self.request.query_params.get("name")
        description = self.request.query_params.get("description")

        if category:
            queryset = queryset.filter(category=category)
        if price:
            queryset = queryset.filter(price=price)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if description:
            queryset = queryset.filter(description__icontains=description)

        return queryset

    def get_cache_key(self, request):
        filters_data = request.query_params.dict()
        limit = request.query_params.get("limit", self.default_limit)
        offset = request.query_params.get("offset", self.default_offset)
        cache_key = f"product_list_{limit}_{offset}_{filters_data}"
        return cache_key

    def perform_create(self, serializer):
        product = serializer.save()

        index_product_task.delay(product.id)

        return product

    @swagger_auto_schema(tags=["Products"])
    def get(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        cached_product_list = cache.get(cache_key)

        if cached_product_list:
            return Response(cached_product_list)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)
        return response

    @swagger_auto_schema(tags=["Products"])
    def post(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        invalidate_product_cache()
        return Response(response.data, status=status.HTTP_201_CREATED)
