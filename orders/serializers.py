from rest_framework import serializers

from products.models import Product
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
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "address", "items"]
        read_only_fields = ["user", "status", "total_price"]

    def get_total_price(self, order):
        # Calculate the total price from the items in the order
        return sum(item.quantity * item.price_at_purchase for item in order.items.all())

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


class AddOrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        """
        Ensure the quantity is less than or equal to the stock of the product.
        """
        product = self.initial_data.get("product")
        product_instance = Product.objects.get(id=product)

        if value > product_instance.stock:
            raise serializers.ValidationError(
                f"Only {product_instance.stock} items are available in stock."
            )
        return value


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        order = self.instance
        if not order.can_change_status(value):
            raise serializers.ValidationError(
                f"Cannot change status from {order.status} to {value}."
            )
        return value
