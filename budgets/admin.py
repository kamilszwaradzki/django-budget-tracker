from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Account, Category

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
