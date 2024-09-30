import redis
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer

redis_instance = redis.StrictRedis(host="127.0.0.1", port=6379, db=1)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(tags=["Categories"])
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Categories"])
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(tags=["Categories"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Categories"])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Categories"])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Categories"])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CategoryRetrieveBySlugView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    @swagger_auto_schema(tags=["Categories"])
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(tags=["Products"])
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Products"])
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(tags=["Products"])
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Products"])
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Products"])
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Products"])
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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
            print("redis")
            queryset = cache.get(cache_key)
            return Response(queryset)
        else:
            print("db")
            queryset = Product.objects.all()
            if slug is not None:
                queryset = queryset.filter(slug__contains=slug)
                serializer = ProductSerializer(queryset, many=True)
                cache.set(cache_key, serializer.data, timeout=60 * 60)

                return Response(serializer.data)


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Set the user from the request

    @swagger_auto_schema(tags=["Review"])
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Review.objects.filter(product_id=product_id)

    @swagger_auto_schema(tags=["Review"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
