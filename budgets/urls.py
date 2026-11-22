from django.urls import path

from budgets.views import CategoryListCreateView, TransactionListCreateView, api_root

urlpatterns = [
    path("", api_root, name="api-root"),
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list",
    ),
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="category-list",
    ),
]
