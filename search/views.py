# Create your views here.
from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from users.documents import UserDocument
from users.serializers import UserListSerializer as UserSerializer

userSearch = UserDocument.search()


class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
    def get(self, request):
        query = request.query_params.get("query", None)
        if query is None:
            return Response(
                {"error": "Please provide a query parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q = Q(
            "multi_match",
            query=query,
            fields=["username", "email"],
            fuzziness="AUTO",
            type="best_fields",
            operator="or",
        )
        search = userSearch.query(q)

        results = search.to_queryset()
        page = self.paginate_queryset(results, request)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(results, many=True)
        return Response(serializer.data)
