from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl.analysis import CustomAnalyzer

from products.models import Product

lowercase_analyzer = CustomAnalyzer(
    "standard", filter=["lowercase"], tokenizer="standard"
)

product_index = Index("products")


@registry.register_document
class ProductDocument(Document):
    category = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(
                analyzer=lowercase_analyzer
            ),  # Apply lowercase analyzer here
            "slug": fields.KeywordField(),
        }
    )

    suggest = fields.CompletionField()

    class Index:
        name = "products"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "tokenizer": {
                    "lowercase_tokenizer": {
                        "type": "pattern",
                        "pattern": "[\\W_]+",  # Tokenize based on non-alphanumeric characters
                    }
                },
                "filter": {
                    "lowercase": {
                        "type": "lowercase",  # Lowercase filter
                    }
                },
                "analyzer": {
                    "standard_lowercase": {
                        "tokenizer": "lowercase_tokenizer",
                        "filter": [
                            "lowercase"
                        ],  # Use lowercase filter to normalize text
                    }
                },
            },
        }

    class Django:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "sell_price",
            "on_sell",
            "stock",
            "image",
            "created_at",
            "updated_at",
        ]

    def get_suggest_field(self, instance):
        # Suggest field can use the product name or other relevant fields
        return {
            "input": [
                instance.name.lower(),
                instance.category.name.lower(),
            ],  # Convert inputs to lowercase
            "weight": 1,
        }

    def prepare_suggest(self, instance):
        return self.get_suggest_field(instance)
