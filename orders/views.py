from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem
from .serializers import (
    AddOrderItemSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(tags=["Order"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Order"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return (
                Order.objects.none()
            )  # Return an empty queryset for schema generation

        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(tags=["Order"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Order"])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Order"])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Order"])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Check if the order status is 'pending'
        if order.status != "pd":
            return Response(
                {"detail": "You can only update orders that are pending."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()

        # Check if the order status is 'pending'
        if order.status != "pd":
            return Response(
                {"detail": "You can only update orders that are pending."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().partial_update(request, *args, **kwargs)


class AddOrderItemView(APIView):
    @swagger_auto_schema(tags=["Order"], request_body=AddOrderItemSerializer)
    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "pd":
            raise PermissionDenied("You can only add items to orders that are pending.")

        serializer = AddOrderItemSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.validated_data["product"]
            quantity = serializer.validated_data["quantity"]

            # Create or update the OrderItem
            order_item, item_created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={
                    "quantity": quantity,
                    "price_at_purchase": (
                        product.sell_price if product.on_sell else product.price
                    ),
                },
            )

            if not item_created:
                # If the item already exists, update the quantity
                order_item.quantity += quantity
                order_item.save()

            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromOrderView(APIView):

    @swagger_auto_schema(tags=["Order"])
    def delete(self, request, order_id, product_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "pd":
            raise PermissionDenied("You can only add items to orders that are pending.")

        order_item = OrderItem.objects.filter(
            order__user=request.user, product_id=product_id
        )

        if not order_item:
            return Response(
                {"detail": "Item not found in this order."},
                status=status.HTTP_404_NOT_FOUND,
            )

        order_item.delete()
        return Response(
            {"detail": "Item removed from order successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["Order"], request_body=OrderStatusUpdateSerializer)
    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderStatusUpdateSerializer(order, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Order status updated successfully",
                    "order": serializer.data,
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
