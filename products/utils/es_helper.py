from django.conf import settings


class ESHelper:
    @classmethod
    def _format_search_results(cls, search_results, query=None, limit=10, offset=0):
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
            "next": (
                cls._get_pagination_link(query, search_results, limit, offset)
                if query
                else None
            ),
            "previous": (
                cls._get_previous_pagination_link(query, offset, limit)
                if query
                else None
            ),
            "results": products,
        }

    @classmethod
    def _get_pagination_link(cls, query, search_results, limit, offset):
        total = search_results.hits.total.value
        if (offset + limit) >= total:
            return None
        return f"?q={query}&limit={limit}&offset={offset + limit}"

    @classmethod
    def _get_previous_pagination_link(cls, query, offset, limit):
        if offset == 0:
            return None
        return f"?q={query}&limit={limit}&offset={max(0, offset - limit)}"
