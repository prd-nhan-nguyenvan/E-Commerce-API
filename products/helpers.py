from django.core.cache import cache


def invalidate_product_cache():
    keys = cache.keys("product_list_*")
    for key in keys:
        cache.delete(key)
