from django.urls import path

from carts.views import AddToCartView, GetCartView, RemoveFromCartView

urlpatterns = [
    path("", GetCartView.as_view(), name="get_cart"),
    path("add/", AddToCartView.as_view(), name="add_to_cart"),
    path(
        "remove/<int:product_id>/",
        RemoveFromCartView.as_view(),
        name="remove_from_cart",
    ),
]
