from django.core.cache import cache
from rest_framework.pagination import LimitOffsetPagination

from products.models import Category
from products.serializers import CategorySerializer


class CategoryService:
    @classmethod
    def get_cached_category_list(cls, request):
        """
        Fetch a paginated list of categories from the database with caching.
        """
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))

        # Generate a unique cache key based on offset and limit
        cache_key = f"category_list_{offset}_{limit}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data
        # Query the database for categories
        categories = Category.objects.all()

        # Use DRF's pagination utility
        paginator = LimitOffsetPagination()
        paginator.default_limit = limit
        paginated_categories = paginator.paginate_queryset(categories, request)

        # Serialize the paginated data
        serializer = CategorySerializer(paginated_categories, many=True)

        # Cache the paginated data
        cache.set(
            cache_key,
            {
                "count": paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            },
        )

        # Return the paginated response
        return {
            "count": paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }

    @classmethod
    def invalidate_category_cache(cls):
        """
        Invalidate all cached category lists by deleting related keys.
        """
        cache.delete_pattern("category_list_*")
