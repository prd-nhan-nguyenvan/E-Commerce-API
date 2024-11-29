from django.urls import include
from django.urls import re_path as url
from rest_framework import routers

from search.views import ProductSuggestionSearchViewSet

router = routers.SimpleRouter(trailing_slash=True)

# Register viewsets
router.register(r"", ProductSuggestionSearchViewSet, basename="product")

urlpatterns = [
    url("", include(router.urls)),
]
