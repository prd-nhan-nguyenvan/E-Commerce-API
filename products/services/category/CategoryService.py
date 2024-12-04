from django.core.cache import cache

from core.services.BaseService import BaseService
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

        cache_key = f"category_list_{offset}_{limit}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        categories = Category.objects.only("id", "name", "slug", "description")
        data = BaseService.paginate(categories, request, CategorySerializer)
        cache.set(cache_key, data)

        return data

    @classmethod
    def get_category(cls, pk):
        """
        Fetch a single category by primary key.
        """
        category = Category.objects.filter(pk=pk).first()
        if not category:
            return None  # or raise an exception if preferred
        return category

    @classmethod
    def invalidate_category_cache(cls):
        """
        Invalidate all cached category lists by deleting related keys.
        """
        cache.delete_pattern("category_list_*")
