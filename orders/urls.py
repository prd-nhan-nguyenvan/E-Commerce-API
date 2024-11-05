from django.urls import path

from .views import (
    AddOrderItemView,
    AdminOrderListView,
    AdminOrderRetrieveUpdateDestroyView,
    AdminOrderStatusUpdateView,
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView,
    OrderStatusUpdateView,
    RemoveFromOrderView,
)

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("<int:pk>/", OrderRetrieveUpdateDestroyView.as_view(), name="order-detail"),
    path("<int:order_id>/add/", AddOrderItemView.as_view(), name="add-order-item"),
    path(
        "<int:order_id>/update-status/",
        OrderStatusUpdateView.as_view(),
        name="update-order-status",
    ),
    path(
        "<int:order_id>/remove/<int:product_id>",
        RemoveFromOrderView.as_view(),
        name="add-order-item",
    ),
    path("admin/lists/", AdminOrderListView.as_view(), name="admin-order-list"),
    path(
        "admin/lists/<int:pk>/",
        AdminOrderRetrieveUpdateDestroyView.as_view(),
        name="admin-order-detail",
    ),
    path(
        "admin/lists/<int:order_id>/update-status/",
        AdminOrderStatusUpdateView.as_view(),
        name="admin-update-order-status",
    ),
]
