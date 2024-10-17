import csv
from io import StringIO

from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdminOrStaff
from ecommerce_project import settings

from .helpers import invalidate_product_cache
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from .tasks import bulk_import_products


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(tags=["Categories"])
    def get(self, request, *args, **kwargs):
        cache_key = "category_list"
        if cache_key in cache:
            data = cache.get(cache_key)
        else:

            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=60 * 60)
            data = response.data
        return Response(data)

    @swagger_auto_schema(tags=["Categories"])
    def post(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete("category_list")
        return Response(response.data, status=status.HTTP_201_CREATED)


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStaff]

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(tags=["Categories"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Categories"])
    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete("category_list")
        return Response(response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Categories"])
    def patch(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        cache.delete("category_list")
        return Response(response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Categories"])
    def delete(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        cache.delete("category_list")
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryRetrieveBySlugView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    @swagger_auto_schema(tags=["Categories"])
    def get(self, request, slug, *args, **kwargs):
        cache_key = f"category_{slug}"
        cached_category = cache.get(cache_key)

        if cached_category:
            return Response(cached_category)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)  # Cache for 1 hour
        return response


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["category", "price"]
    ordering_fields = ["name", "price", "created_at"]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    @swagger_auto_schema(tags=["Products"])
    def get(self, request, *args, **kwargs):
        default_limit = getattr(settings, "DEFAULT_LIMIT", 10)
        default_offset = getattr(settings, "DEFAULT_OFFSET", 0)

        limit = request.query_params.get("limit", default_limit)
        offset = request.query_params.get("offset", default_offset)

        filters_data = request.query_params.dict()  # All query params for cache key
        cache_key = f"product_list_{limit}_{offset}_{filters_data}"

        cached_product_list = cache.get(cache_key)

        if cached_product_list:
            return Response(cached_product_list)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)  # Cache for 1 hour
        return response

    @swagger_auto_schema(tags=["Products"])
    def post(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        invalidate_product_cache()
        return Response(response.data, status=status.HTTP_201_CREATED)


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
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Products"])
    def put(self, request, *args, **kwargs):
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

        return Response(response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Products"])
    def patch(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        invalidate_product_cache()
        return Response(response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Products"])
    def delete(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        invalidate_product_cache()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductRetrieveBySlugView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(tags=["Products"])
    def get(self, request, slug, *args, **kwargs):
        if slug is not None:
            cache_key = "slug" + slug
        else:
            cache_key = "slug"

        if cache_key in cache:

            queryset = cache.get(cache_key)
            return Response(queryset)
        else:

            queryset = Product.objects.all()
            if slug is not None:
                queryset = queryset.filter(slug__contains=slug).first()
                serializer = self.get_serializer(queryset)
                cache.set(cache_key, serializer.data, timeout=60 * 60)

                return Response(serializer.data)


class BulkImportProductView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminOrStaff]

    @swagger_auto_schema(
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="CSV file with product data",
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_data = file.read().decode("utf-8")
            csv_data = csv.DictReader(StringIO(file_data))
            product_data_list = [row for row in csv_data]
            bulk_import_products.delay(product_data_list)
            return Response(
                {"message": "Products import started."},
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Set the user from the request

    @swagger_auto_schema(tags=["Review"])
    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        if not product_id:
            return Response(
                {"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        cache_key = f"product_{product_id}_reviews"
        cache.delete(cache_key)
        return super().create(request, *args, **kwargs)


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Review.objects.filter(product_id=product_id)

    @swagger_auto_schema(tags=["Review"])
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs["product_id"]
        cache_key = f"product_{product_id}_reviews"
        cached_reviews = cache.get(cache_key)

        if cached_reviews:
            return Response(cached_reviews)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)  # Cache for 1 hour
        return response
