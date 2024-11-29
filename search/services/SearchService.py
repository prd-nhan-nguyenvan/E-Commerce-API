from elasticsearch.exceptions import ElasticsearchException
from elasticsearch_dsl import Q, Search


class SearchService:
    @classmethod
    def get_suggestions(cls, query: str, limit: int) -> list:
        try:

            query = query.lower()

            search = Search(using="default", index="products")

            search = search.suggest(
                "suggestion", query, completion={"field": "suggest", "size": limit}
            )

            response = search.execute()

            suggestions = [
                suggest["text"] for suggest in response.suggest.suggestion[0].options
            ]

            if not suggestions:

                fuzzy_search = Search(using="default", index="products")
                fuzzy_search = fuzzy_search.query(
                    Q(
                        "multi_match",
                        query=query,
                        fields=["name", "description", "slug"],
                        fuzziness="AUTO",
                    )
                )

                fuzzy_response = fuzzy_search.execute()

                suggestions = [hit.name for hit in fuzzy_response]

            suggestions = suggestions[:limit]

            return suggestions

        except ElasticsearchException:

            return []

        except Exception:

            return []
