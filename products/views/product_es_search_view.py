from django.conf import settings
from django.core.cache import cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from elasticsearch_dsl.query import MultiMatch
from rest_framework import permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from products.documents import ProductDocument
from products.serializers import ProductSearchResponseSerializer


class ProductESSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination

    @swagger_auto_schema(
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search query",
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Limit for pagination",
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Offset for pagination",
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful product search response",
                schema=ProductSearchResponseSerializer(),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Search query is required.",
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q")
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        if not query:
            return self._bad_request("Search query is required.")

        cached_result = self._get_cached_result(query, limit, offset)
        if cached_result:
            return Response(cached_result, status=status.HTTP_200_OK)

        search_results = self._search_products(query, limit, offset)
        formatted_results = self._format_search_results(
            search_results, query, limit, offset
        )

        self._cache_results(query, limit, offset, formatted_results)

        return Response(formatted_results, status=status.HTTP_200_OK)

    def _get_limit(self, request):
        return int(request.query_params.get("limit", 10))

    def _get_offset(self, request):
        return int(request.query_params.get("offset", 0))

    def _bad_request(self, message):
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    def _get_cached_result(self, query, limit, offset):
        cache_key = f"search_products_{query}_{limit}_{offset}"
        return cache.get(cache_key)

    def _search_products(self, query, limit, offset):
        search = ProductDocument.search().query(
            MultiMatch(
                query=query,
                fields=["name", "description", "slug", "category.name"],
                operator="or",
                fuzziness="AUTO",
            )
        )
        search = search[offset : offset + limit]
        return search.execute()

    def _format_search_results(self, search_results, query, limit, offset):
        base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
        products = [
            {
                "id": hit.to_dict().get("id"),
                "category": hit.to_dict().get("category", {}).get("id"),
                "name": hit.to_dict().get("name"),
                "slug": hit.to_dict().get("slug"),
                "description": hit.to_dict().get("description"),
                "price": hit.to_dict().get("price"),
                "sell_price": hit.to_dict().get("sell_price"),
                "on_sell": hit.to_dict().get("on_sell"),
                "stock": hit.to_dict().get("stock"),
                "image": (
                    f"{base_url}{hit.to_dict().get('image')}"
                    if hit.to_dict().get("image")
                    else None
                ),
                "created_at": hit.to_dict().get("created_at"),
                "updated_at": hit.to_dict().get("updated_at"),
            }
            for hit in search_results.hits
        ]

        return {
            "count": search_results.hits.total.value,
            "next": self._get_pagination_link(query, search_results, limit, offset),
            "previous": self._get_previous_pagination_link(query, offset, limit),
            "results": products,
        }

    def _get_pagination_link(self, query, search_results, limit, offset):
        total = search_results.hits.total.value
        if (offset + limit) >= total:
            return None
        return f"?q={query}&limit={limit}&offset={offset + limit}"

    def _get_previous_pagination_link(self, query, offset, limit):
        if offset == 0:
            return None
        return f"?q={query}&limit={limit}&offset={max(0, offset - limit)}"

    def _cache_results(self, query, limit, offset, formatted_results):
        cache_key = f"search_products_{query}_{limit}_{offset}"
        cache.set(cache_key, formatted_results, timeout=60 * 60)
