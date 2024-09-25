from django.urls import path

from carts.views import AddToCartView

urlpatterns = [
    path("add/", AddToCartView.as_view(), name="add-to-cart"),
]
