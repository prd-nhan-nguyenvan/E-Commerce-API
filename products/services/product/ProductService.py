from django.conf import settings
from django.core.cache import cache

from core.services.BaseService import BaseService
from products.models import Product
from products.serializers import ProductSerializer


class ProductService:
    default_limit = getattr(settings, "DEFAULT_LIMIT", 10)
    default_offset = getattr(settings, "DEFAULT_OFFSET", 0)

    @classmethod
    def get_cache_key(cls, filters, limit, offset):
        """
        Generate a cache key based on query parameters.
        """
        cache_key = f"product_list_{limit}_{offset}_{hash(frozenset(filters.items()))}"
        return cache_key

    @classmethod
    def get_filtered_products(cls, request):
        """
        Retrieve filtered products with pagination and caching.
        """
        filters = {
            key: value
            for key, value in request.query_params.items()
            if key in ["category", "price", "name", "description"]
        }
        limit = int(request.query_params.get("limit", ProductService.default_limit))
        offset = int(request.query_params.get("offset", ProductService.default_offset))

        # Generate cache key
        cache_key = cls.get_cache_key(filters, limit, offset)
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        # Filter products based on provided filters
        queryset = Product.objects.select_related("category").only(
            "id", "name", "description", "price", "created_at", "category_id"
        )
        if "category" in filters:
            queryset = queryset.filter(category=filters["category"])
        if "price" in filters:
            queryset = queryset.filter(price=filters["price"])
        if "name" in filters:
            queryset = queryset.filter(name__icontains=filters["name"])
        if "description" in filters:
            queryset = queryset.filter(description__icontains=filters["description"])

        # Paginate the results
        data = BaseService.paginate(queryset, request, ProductSerializer)
        cache.set(cache_key, data)
        return data

    @classmethod
    def create_product(cls, validated_data):
        """
        Create a new product and trigger any necessary tasks.
        """
        product = Product.objects.create(**validated_data)
        return product
