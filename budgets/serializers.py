from rest_framework import serializers

from budgets.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "category",
            "amount",
            "date",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
