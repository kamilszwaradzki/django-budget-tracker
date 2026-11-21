from rest_framework import serializers

from budgets.models import Account, Category, Transaction


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

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            fields["account"].queryset = Account.objects.filter(owner=request.user)
            fields["category"].queryset = Category.objects.filter(owner=request.user)
        return fields
