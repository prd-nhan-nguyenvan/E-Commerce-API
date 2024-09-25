from rest_framework import serializers

from users.models import UserProfile

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price_at_purchase"]
        read_only_fields = ["price_at_purchase"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    address = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "address", "items"]
        read_only_fields = ["user", "status", "total_price"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        user = self.context["request"].user
        user_profile = UserProfile.objects.get(user=user)
        validated_data["address"] = validated_data.get("address", user_profile.address)

        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = item_data["product"]

            item_data["price_at_purchase"] = (
                product.sell_price if product.on_sell else product.price
            )

            OrderItem.objects.create(order=order, **item_data)
        return order

    def validate(self, data):
        # Add validation logic if needed
        return data
