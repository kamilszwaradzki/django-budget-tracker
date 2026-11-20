from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


class User(AbstractUser):
    pass


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Account(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    name = models.CharField(max_length=100)
    currency = models.CharField(
        max_length=3,
        default="PLN",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{3}$",
                message="Currency must be a valid three-letter uppercase code.",
            ),
        ],
    )
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Category(TimeStampedModel):

    class Type(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=7,
        choices=Type.choices,
    )

    class Meta:
        ordering = ["type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name", "type"],
                name="budgets_category_owner_name_type_unique",
            ),
        ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(TimeStampedModel):
    account = models.ForeignKey(
        "budgets.Account",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.ForeignKey(
        "budgets.Category",
        on_delete=models.RESTRICT,
        related_name="transactions",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    date = models.DateField()
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["-date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(amount=0),
                name="budgets_transaction_amount_nonzero",
            )
        ]

    def __str__(self):
        return f"{self.date} - {self.category.name} - {self.amount}"
