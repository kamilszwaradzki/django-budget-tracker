from rest_framework.generics import ListCreateAPIView

from budgets.models import Transaction
from budgets.serializers import TransactionSerializer


class TransactionListView(ListCreateAPIView):
    serializer_class = TransactionSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return (
            Transaction.objects
            .filter(account__owner=self.request.user)
            .select_related("account", "category")
        )
