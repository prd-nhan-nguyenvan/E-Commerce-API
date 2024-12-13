from django.conf import settings
from django.core.cache import cache
from elasticsearch_dsl.query import MultiMatch

from core.services.BaseService import BaseService
from products.documents import ProductDocument
from products.models import Product
from products.serializers import ProductSerializer
from products.tasks import delete_product_from_es, index_product_task
from products.utils.invalidate_product_cache_helpers import invalidate_product_cache


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
            if key in ["category", "price_lt", "price_gt", "name", "description"]
            and value != ""
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
        if "price_lt" in filters:
            queryset = queryset.filter(price__lt=filters["price_lt"])
        if "price_gt" in filters:
            queryset = queryset.filter(price__gt=filters["price_gt"])
        # Elasticsearch keyword search
        keyword = filters.get("name") or filters.get("description")
        if keyword:
            search = ProductDocument.search().query(
                MultiMatch(
                    query=keyword,
                    fields=["name", "description"],
                    operator="or",
                    fuzziness="AUTO",
                )
            )
            search_results = search.execute()
            product_ids = [hit.meta.id for hit in search_results]
            queryset = queryset.filter(id__in=product_ids)

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

        # Trigger background tasks
        cls._post_update_product(product)
        return product

    @classmethod
    def _post_update_product(cls, product):
        """
        Trigger tasks after updating a product.
        """
        index_product_task.delay(product.id)
        invalidate_product_cache()
        return product

    @classmethod
    def get_product(cls, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    @classmethod
    def update_product(cls, product, data):
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cls._post_update_product(product)
            return serializer.data, None
        return None, serializer.errors

    @classmethod
    def delete_product(cls, product):
        product_id = product.id
        product.delete()
        invalidate_product_cache()
        delete_product_from_es.delay(product_id)
