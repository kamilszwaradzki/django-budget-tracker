from rest_framework.generics import ListCreateAPIView

from budgets.models import Transaction
from budgets.serializers import TransactionSerializer
from budgets.services import create_transaction


class TransactionListCreateView(ListCreateAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(account__owner=self.request.user)

    def perform_create(self, serializer):
        new_transaction = create_transaction(
            user=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = new_transaction
