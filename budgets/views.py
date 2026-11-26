from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from budgets.models import Category, Transaction
from budgets.serializers import CategorySerializer, TransactionSerializer
from budgets.services import (
    create_category,
    create_transaction,
    delete_category,
    update_category,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response(
        {
            "transactions": reverse("transaction-list", request=request, format=format),
            "categories": reverse("category-list", request=request, format=format),
        }
    )


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


class CategoryListCreateView(ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        new_category = create_category(
            user=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = new_category


class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        new_category = update_category(
            category=serializer.instance,
            **serializer.validated_data,
        )
        serializer.instance = new_category

    def perform_destroy(self, instance):
        delete_category(category=instance)
