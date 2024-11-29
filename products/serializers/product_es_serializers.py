from rest_framework import serializers

from products.serializers.product_serializers import ProductSerializer


class ProductSearchResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True, required=False)
    previous = serializers.CharField(allow_null=True, required=False)
    results = ProductSerializer(many=True)
