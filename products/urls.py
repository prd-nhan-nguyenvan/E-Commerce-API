from django.urls import path

from .views import (
    CategoryListCreateView,
    CategoryRetrieveBySlugView,
    CategoryRetrieveUpdateDestroyView,
    ProductListCreateView,
    ProductRetrieveBySlugView,
    ProductRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path(
        "categories/<int:pk>/",
        CategoryRetrieveUpdateDestroyView.as_view(),
        name="category-detail",
    ),
    path(
        "categories/slug/<slug:slug>/",
        CategoryRetrieveBySlugView.as_view(),
        name="category-detail-by-slug",
    ),
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "products/<int:pk>/",
        ProductRetrieveUpdateDestroyView.as_view(),
        name="product-detail",
    ),
    path(
        "products/slug/<slug:slug>/",
        ProductRetrieveBySlugView.as_view(),
        name="product-detail-by-slug",
    ),
]
