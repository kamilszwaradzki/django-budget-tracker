from django.urls import path

from budgets.views import TransactionListView

urlpatterns = [
    path(
        "transactions/",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
]
