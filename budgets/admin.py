from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Account, Category, Transaction, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "currency",
        "initial_balance",
        "created_at",
    )
    list_filter = ("currency",)
    search_fields = ("name", "owner__username")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "type",
        "created_at",
    )
    list_filter = ("type",)
    search_fields = ("name", "owner__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "account",
        "category",
        "amount",
        "created_at",
    )
    list_filter = (
        "category",
        "account",
        "date",
    )
    date_hierarchy = "date"
    search_fields = (
        "description",
        "account__name",
        "category__name",
    )
    list_select_related = (
        "account",
        "category",
    )
