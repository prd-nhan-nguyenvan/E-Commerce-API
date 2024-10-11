from django.urls import path

from search.views import PaginatedElasticSearchAPIView

urlpatterns = [
    path("user/", PaginatedElasticSearchAPIView.as_view(), name="search"),
]
