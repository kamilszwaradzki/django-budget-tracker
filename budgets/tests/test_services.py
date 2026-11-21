import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from budgets.services import create_transaction

DATE = datetime.date(2026, 11, 20)


def test_create_transaction_expense_valid_data_creates_transaction(
    user, account, expense_category
):
    new_transaction = create_transaction(
        user=user,
        account=account,
        category=expense_category,
        amount=Decimal("-12.50"),
        date=DATE,
    )

    assert new_transaction.pk is not None
    assert new_transaction.amount == Decimal("-12.50")
    assert new_transaction.account == account
    assert new_transaction.category == expense_category
    assert new_transaction.created_at is not None


def test_create_transaction_income_with_negative_amount_raises(
    user, account, income_category
):
    with pytest.raises(ValidationError) as exc_info:
        create_transaction(
            user=user,
            account=account,
            category=income_category,
            amount=Decimal("-1.00"),
            date=DATE,
        )

    assert "amount" in exc_info.value.message_dict


def test_create_transaction_expense_with_positive_amount_raises(
    user, account, expense_category
):
    with pytest.raises(ValidationError) as exc_info:
        create_transaction(
            user=user,
            account=account,
            category=expense_category,
            amount=Decimal("1.00"),
            date=DATE,
        )

    assert "amount" in exc_info.value.message_dict


def test_create_transaction_account_of_other_user_raises(
    user, other_account, expense_category
):
    with pytest.raises(ValidationError) as exc_info:
        create_transaction(
            user=user,
            account=other_account,
            category=expense_category,
            amount=Decimal("-5.00"),
            date=DATE,
        )

    assert "account" in exc_info.value.message_dict


def test_create_transaction_category_of_other_user_raises(
    user, account, other_expense_category
):
    with pytest.raises(ValidationError) as exc_info:
        create_transaction(
            user=user,
            account=account,
            category=other_expense_category,
            amount=Decimal("-5.00"),
            date=DATE,
        )

    assert "category" in exc_info.value.message_dict


def test_create_transaction_zero_amount_raises(user, account, expense_category):
    with pytest.raises(ValidationError) as exc_info:
        create_transaction(
            user=user,
            account=account,
            category=expense_category,
            amount=Decimal("0.00"),
            date=DATE,
        )

    assert "amount" in exc_info.value.message_dict
