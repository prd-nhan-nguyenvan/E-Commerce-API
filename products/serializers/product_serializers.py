from rest_framework import serializers

from products.models import Product


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
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        price = data.get("price")
        sell_price = data.get("sell_price")

        if price is not None and price < 0:
            raise serializers.ValidationError({"price": "Price cannot be negative."})

        if sell_price is not None and sell_price < 0:
            raise serializers.ValidationError(
                {"sell_price": "Sell price cannot be negative."}
            )

        # If updating, get the current instance's price
        if self.instance:
            current_price = self.instance.price
            current_sell_price = self.instance.sell_price
        else:
            current_price = None
            current_sell_price = None

        if price is not None and sell_price is not None:
            if price < sell_price:
                raise serializers.ValidationError(
                    {"price": "Price cannot be less than the sell price."}
                )
        # Ensure sell price is not greater than the price
        elif sell_price is not None and current_price is not None:
            if sell_price > current_price:
                raise serializers.ValidationError(
                    {
                        "sell_price": "Sell price cannot be greater than the regular price."
                    }
                )
        elif price is not None and current_sell_price is not None:
            if price < current_sell_price:
                raise serializers.ValidationError(
                    {"price": "Price cannot be less than the sell price."}
                )

        return data
