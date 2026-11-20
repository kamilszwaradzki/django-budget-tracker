from django.urls import path

from budgets.views import TransactionListCreateView

urlpatterns = [
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list",
    ),
]
