from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "slug",
            "description",
            "price",
            "sell_price",
            "on_sell",
            "stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        price = data.get("price", self.instance.price)
        sell_price = data.get("sell_price", self.instance.sell_price)

        if price is not None and price < 0:
            raise serializers.ValidationError({"price": "Price cannot be negative."})

        if sell_price is not None and sell_price < 0:
            raise serializers.ValidationError(
                {"sell_price": "Sell price cannot be negative."}
            )

        # Ensure sell price is not greater than the price
        if sell_price > price:
            raise serializers.ValidationError(
                {"sell_price": "Sell price cannot be greater than the regular price."}
            )

        return data
