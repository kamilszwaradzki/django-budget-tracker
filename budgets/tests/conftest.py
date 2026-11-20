import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from budgets.models import Account, Category


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="alice", password="pass"
    )


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(
        username="bob", password="pass"
    )


@pytest.fixture
def account(user):
    return Account.objects.create(owner=user, name="Alice Wallet")


@pytest.fixture
def expense_category(user):
    return Category.objects.create(
        owner=user, name="Food", type=Category.Type.EXPENSE
    )


@pytest.fixture
def income_category(user):
    return Category.objects.create(
        owner=user, name="Salary", type=Category.Type.INCOME
    )


@pytest.fixture
def other_account(other_user):
    return Account.objects.create(owner=other_user, name="Bob Wallet")


@pytest.fixture
def other_expense_category(other_user):
    return Category.objects.create(
        owner=other_user, name="Bob Food", type=Category.Type.EXPENSE
    )


@pytest.fixture
def api_client():
    return APIClient()
