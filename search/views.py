from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from users.documents import UserDocument

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
            fields=["username", "email", "role"],
            fuzziness="AUTO",
            type="best_fields",
            operator="or",
        )
        search = userSearch.query(q)
        response = search.execute()

        results = [hit.to_dict() for hit in response]
        page = self.paginate_queryset(results, request)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(results)
