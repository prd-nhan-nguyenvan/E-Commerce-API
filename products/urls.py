from django.urls import path

from products.views import (
    BulkImportProductView,
    CategoryListCreateView,
    CategoryRetrieveBySlugView,
    CategoryRetrieveUpdateDestroyView,
    ProductESSearchView,
    ProductListCreateView,
    ProductRetrieveBySlugView,
    ProductRetrieveUpdateDestroyView,
    ProductReviewListView,
    ReviewCreateView,
    SimilarProductView,
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
    path(
        "products/bulk-import/",
        BulkImportProductView.as_view(),
        name="bulk-import-products",
    ),
    path("products/search/", ProductESSearchView.as_view(), name="product-search"),
    path(
        "products/<int:product_id>/similar/",
        SimilarProductView.as_view(),
        name="similar-products",
    ),
    path(
        "products/<int:product_id>/reviews/",
        ProductReviewListView.as_view(),
        name="product-reviews",
    ),
    path("reviews/", ReviewCreateView.as_view(), name="create-review"),
]
