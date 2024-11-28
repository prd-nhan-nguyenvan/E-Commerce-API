from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsAdminOrStaff
from products.models import Category, Product, Review
from products.serializers import CategorySerializer, ProductSerializer, ReviewSerializer


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
        cache.set(cache_key, response.data, timeout=60 * 60)
        return response


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


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
        cache.set(cache_key, response.data, timeout=60 * 60)
        return response
