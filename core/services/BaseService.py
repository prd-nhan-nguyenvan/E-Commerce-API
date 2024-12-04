from rest_framework.pagination import LimitOffsetPagination


class BaseService:
    @staticmethod
    def paginate(queryset, request, serializer_class):
        paginator = LimitOffsetPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)
        serialized_data = serializer_class(paginated_data, many=True)
        return {
            "count": paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serialized_data.data,
        }
