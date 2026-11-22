import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import Account, Category, Transaction, User


def _validate_transaction_data(
    *,
    user: User,
    account: Account,
    category: Category,
    amount: Decimal,
) -> None:
    errors = {}

    if account.owner_id != user.pk:
        errors["account"] = "Account must belong to the current user."

    if category.owner_id != user.pk:
        errors["category"] = "Category must belong to the current user."

    if category.type == Category.Type.INCOME and amount <= 0:
        errors["amount"] = "Income transactions must have a positive amount."

    elif category.type == Category.Type.EXPENSE and amount >= 0:
        errors["amount"] = "Expense transactions must have a negative amount."

    if errors:
        raise ValidationError(errors)


def create_transaction(
    *,
    user: User,
    account: Account,
    category: Category,
    amount: Decimal,
    date: datetime.date,
    description: str = "",
) -> Transaction:
    _validate_transaction_data(
        user=user,
        account=account,
        category=category,
        amount=amount,
    )

    new_transaction = Transaction(
        account=account,
        category=category,
        amount=amount,
        date=date,
        description=description,
    )

    new_transaction.full_clean()
    new_transaction.save()

    return new_transaction


def create_category(
    *,
    user: User,
    name: str,
    type: Category.Type,
) -> Category:

    new_category = Category(
        owner=user,
        name=name.strip(),
        type=type,
    )

    new_category.full_clean()

    try:
        with transaction.atomic():
            new_category.save()
    except IntegrityError as exc:
        raise ValidationError(
            {"__all__": ["Category with this name and type already exists."]}
        ) from exc

    return new_category
