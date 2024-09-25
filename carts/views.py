from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AddToCartSerializer, CartItemSerializer


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
