import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from budgets.models import Transaction

DATE = datetime.date(2026, 11, 20)


def test_full_clean_rejects_zero_amount(account, expense_category):
    transaction = Transaction(
        account=account,
        category=expense_category,
        amount=Decimal("0.00"),
        date=DATE,
    )

    with pytest.raises(ValidationError):
        transaction.full_clean()
