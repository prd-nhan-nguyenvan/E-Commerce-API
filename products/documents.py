from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry

from .models import Product

product_index = Index("products")


@registry.register_document
class ProductDocument(Document):
    # Define the 'category' field using fields.ObjectField to include related data
    category = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
            "slug": fields.TextField(),
        }
    )

    class Index:
        name = "products"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Product  # The model associated with this Document
        # Fields of the model to index
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
