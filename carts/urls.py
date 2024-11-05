from django.urls import path

from carts.views import (
    AddToCartView,
    EmptyCartView,
    GetCartView,
    UpdateRemoveCartItemView,
)

urlpatterns = [
    path("", GetCartView.as_view(), name="get-cart"),
    path("items/", AddToCartView.as_view(), name="add-to-cart"),
    path(
        "items/<int:product_id>/",
        UpdateRemoveCartItemView.as_view(),
        name="update-remove-from-cart",
    ),
    path(
        "empty/",
        EmptyCartView.as_view(),
        name="empty-cart",
    ),
]
