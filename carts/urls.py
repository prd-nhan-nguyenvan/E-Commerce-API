from django.urls import path

from carts.views import AddToCartView, GetCartView

urlpatterns = [
    path("", GetCartView.as_view(), name="get-cart"),
    path("add/", AddToCartView.as_view(), name="add-to-cart"),
]
