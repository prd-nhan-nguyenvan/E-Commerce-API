from django.urls import path

from .views import (
    CategoryListCreateView,
    CategoryRetrieveBySlugView,
    CategoryRetrieveUpdateDestroyView,
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
]
