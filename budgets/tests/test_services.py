import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from budgets.errors import CategoryInUseError
from budgets.models import Category, Transaction
from budgets.services import (
    create_category,
    create_transaction,
    delete_category,
    update_category,
)

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
            name="  ",
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


def test_update_category_name(expense_category):
    update_category(
        category=expense_category, name="New name"
    )

    expense_category.refresh_from_db()

    assert expense_category.name == "New name"


def test_update_category_duplicate_name(expense_category, income_category):
    with pytest.raises(ValidationError) as exc_info:
        update_category(
            category=income_category,
            name=expense_category.name,
            type=expense_category.type,
        )

    assert "__all__" in exc_info.value.message_dict


def test_update_category_type_with_transactions(user, account, expense_category):
    create_transaction(
        user=user,
        account=account,
        category=expense_category,
        amount=Decimal("-1.0"),
        date=DATE,
    )

    with pytest.raises(ValidationError) as exc:
        update_category(
            category=expense_category,
            name=expense_category.name,
            type=Category.Type.INCOME,
        )

    assert "type" in exc.value.message_dict

    expense_category.refresh_from_db()
    assert expense_category.type == Category.Type.EXPENSE


def test_update_category_type_without_transactions(expense_category):
    update_category(
        category=expense_category, name=expense_category.name, type=Category.Type.INCOME
    )

    expense_category.refresh_from_db()

    assert expense_category.type == Category.Type.INCOME


def test_update_category_same_type_with_transactions(user, account, expense_category):
    create_transaction(
        user=user,
        account=account,
        category=expense_category,
        amount=Decimal("-1.0"),
        date=DATE,
    )

    update_category(
        category=expense_category,
        name="Updated name",
        type=Category.Type.EXPENSE,
    )

    expense_category.refresh_from_db()

    assert expense_category.name == "Updated name"
    assert expense_category.type == Category.Type.EXPENSE


def test_delete_category_without_transactions_deletes_category(expense_category):
    category_id = expense_category.pk

    delete_category(category=expense_category)

    assert not Category.objects.filter(pk=category_id).exists()


def test_delete_category_with_transactions_raises_category_in_use(
    user, account, expense_category
):
    create_transaction(
        user=user,
        account=account,
        category=expense_category,
        amount=Decimal("-1.00"),
        date=DATE,
    )

    with pytest.raises(CategoryInUseError):
        delete_category(category=expense_category)


def test_delete_category_with_transactions_keeps_category_and_transactions(
    user, account, expense_category
):
    create_transaction(
        user=user,
        account=account,
        category=expense_category,
        amount=Decimal("-1.00"),
        date=DATE,
    )

    with pytest.raises(CategoryInUseError):
        delete_category(category=expense_category)

    assert Category.objects.filter(pk=expense_category.pk).exists()
    assert Transaction.objects.filter(category=expense_category).count() == 1
