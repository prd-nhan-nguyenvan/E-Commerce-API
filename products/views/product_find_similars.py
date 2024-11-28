import logging

from django.conf import settings
from django.core.cache import cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.documents import ProductDocument
from products.serializers import ProductSearchResponseSerializer

logger = logging.getLogger(__name__)


class SimilarProductView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter(
                "product_id",
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Product ID to find similar products.",
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Limit for pagination",
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful similar product search response",
                schema=ProductSearchResponseSerializer(),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid product ID.",
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs["product_id"]
        limit = int(request.query_params.get("limit", 10))

        cache_key = f"similar_products_{product_id}_{limit}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result, status=status.HTTP_200_OK)

        # Retrieve the product by ID to get its name, category, and description
        try:
            product = ProductDocument.get(id=product_id)
        except Exception as e:
            logger.error(f"Error retrieving product with ID {product_id}: {e}")
            return Response(
                {"error": "Product not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Build the Elasticsearch query
        search = ProductDocument.search().query(
            "bool",
            should=[
                # 1. Find products with similar names (fuzzy matching)
                {"match": {"name": {"query": product.name, "fuzziness": "AUTO"}}},
                # 2. Find products in the same category
                {"term": {"category.id": product.category.id}},
                # 3. Find products with similar terms in the description (more_like_this)
                {
                    "more_like_this": {
                        "fields": ["description"],
                        "like": [{"_id": product_id}],
                        "min_term_freq": 1,
                        "max_query_terms": 10,
                    }
                },
            ],
            minimum_should_match=1,
        )
        search = search[:limit]

        response = search.execute()

        # Format results
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
            for hit in response.hits
        ]

        result = {
            "count": len(products),
            "results": products,
        }

        cache.set(cache_key, result, timeout=60 * 60)  # Cache for 1 hour

        return Response(result, status=status.HTTP_200_OK)
