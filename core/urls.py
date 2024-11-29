from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.urls import re_path as url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from oauth2_provider import urls as oauth2_urls
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce API",
        default_version="v1",
        description="API documentation for E-Commerce project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="nhan.nguyenvan@paradox.ai"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path("o/", include(oauth2_urls)),
    path("api/auth/", include("authentication.urls")),
    path("api/products/", include("products.urls")),
    path("api/users/", include("users.urls")),
    path("api/carts/", include("carts.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/search/", include("search.urls")),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    url(r"^api/products/", include("products.router"), name="products"),
]

# Only serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
