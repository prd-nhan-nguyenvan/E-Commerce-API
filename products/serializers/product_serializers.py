from rest_framework import serializers

from core.settings import BASE_URL, MEDIA_URL
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

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
            "image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {"image": {"required": False}}

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, "url"):
            return obj.image.url
        return "https://static.example.com/images/default.jpg"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        image = instance.image if hasattr(instance, "image") else None
        if image and hasattr(image, "url"):
            data["image_url"] = image.url
        else:
            data["image_url"] = "https://static.example.com/images/default.jpg"
        return data

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

    def build_image_url(self, image_url):
        if BASE_URL in image_url:
            return image_url

        return f"{BASE_URL}{MEDIA_URL}{image_url}"


class PaginatedProductSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_blank=True)
    previous = serializers.CharField(allow_blank=True)
    results = ProductSerializer(many=True)
