from django.urls import path

from budgets.views import TransactionListCreateView, api_root

urlpatterns = [
    path("", api_root, name="api-root"),
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list",
    ),
]
