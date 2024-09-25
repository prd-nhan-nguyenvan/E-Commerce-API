from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart
from .serializers import AddToCartSerializer, CartItemSerializer, CartSerializer


class AddToCartView(APIView):
    @swagger_auto_schema(tags=["Cart"], request_body=AddToCartSerializer)
    def post(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            cart_item = serializer.save()
            return Response(
                {
                    "message": "Item added to cart successfully",
                    "cart": CartItemSerializer(cart_item).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCartView(APIView):
    @swagger_auto_schema(tags=["Cart"])
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response(
                {"detail": "Cart is empty or does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
