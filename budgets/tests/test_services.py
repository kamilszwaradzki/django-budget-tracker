import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from budgets.models import Category
from budgets.services import create_category, create_transaction

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


def test_create_category_valid_data_creates_category(user):
    new_category = create_category(
        user=user,
        name="School",
        type=Category.Type.EXPENSE,
    )

    assert new_category.pk is not None
    assert new_category.owner == user
    assert new_category.name == "School"
    assert new_category.type == Category.Type.EXPENSE
    assert new_category.created_at is not None


def test_create_category_duplicate_name_and_type_raises(user):
    create_category(
        user=user,
        name="School",
        type=Category.Type.EXPENSE,
    )
    with pytest.raises(ValidationError) as exc_info:
        create_category(
            user=user,
            name="School",
            type=Category.Type.EXPENSE,
        )
    assert "__all__" in exc_info.value.message_dict


def test_create_category_whitespace_name_raises(user):
    with pytest.raises(ValidationError) as exc_info:
        create_category(
            user=user,
            name="",
            type=Category.Type.EXPENSE,
        )
    assert "name" in exc_info.value.message_dict


def test_create_category_integrity_error_is_converted_to_validation_error(
    user, monkeypatch
):
    create_category(user=user, name="School2", type=Category.Type.EXPENSE)
    # symulujemy wyścig: walidacja przepuszcza duplikat, który łapie dopiero baza
    monkeypatch.setattr(Category, "full_clean", lambda self, *a, **kw: None)

    with pytest.raises(ValidationError):
        create_category(user=user, name="School2", type=Category.Type.EXPENSE)
