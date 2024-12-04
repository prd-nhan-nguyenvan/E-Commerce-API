from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from search.serializers.SuggestionSeachResponseSerializer import (
    SuggestionSearchResponseSerializer,
)
from search.services import SearchService


class ProductSuggestionSearchViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [AllowAny()]

    @swagger_auto_schema(
        tags=["Search"],
        operation_summary="Get suggestions for search query",
        operation_description="Get suggestions for search query",
        manual_parameters=[
            openapi.Parameter(
                "query",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search query",
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Number of suggestions to return",
            ),
        ],
        responses={200: SuggestionSearchResponseSerializer(), 400: "Bad request"},
    )
    @action(detail=False, methods=["get"])
    def suggest(self, request, *args, **kwargs):
        query = request.query_params.get("query", "")
        if not query:
            return Response({"suggestions": []})
        limit = int(request.query_params.get("limit", 5))
        suggestions = SearchService.get_suggestions(query, limit)

        serializer = SuggestionSearchResponseSerializer(
            data={"suggestions": suggestions}
        )

        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
