import datetime
from decimal import Decimal

from budgets.models import Category, Transaction

URL = "/api/transactions/"
URL_CATEGORY = "/api/categories/"
DATE = "2026-11-20"


def category_url(pk):
    return f"{URL_CATEGORY}{pk}/"


def test_list_transactions_unauthenticated_returns_403(api_client):
    response = api_client.get(URL)

    assert response.status_code == 403


def test_list_transactions_returns_only_current_user_transactions(
    api_client,
    user,
    account,
    expense_category,
    other_user,
    other_account,
    other_expense_category,
):
    Transaction.objects.create(
        account=account,
        category=expense_category,
        amount=Decimal("-1.00"),
        date=datetime.date(2026, 11, 20),
    )
    Transaction.objects.create(
        account=other_account,
        category=other_expense_category,
        amount=Decimal("-2.00"),
        date=datetime.date(2026, 11, 20),
    )

    api_client.force_authenticate(user=user)
    response = api_client.get(URL)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["amount"] == "-1.00"


def test_create_transaction_valid_data_returns_201_and_persists(
    api_client, user, account, expense_category
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL,
        data={
            "account": account.pk,
            "category": expense_category.pk,
            "amount": "-12.50",
            "date": DATE,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["id"] is not None
    assert response.data["created_at"] is not None

    assert Transaction.objects.filter(pk=response.data["id"]).exists()


def test_create_transaction_with_other_users_account_returns_400(
    api_client, user, other_account, expense_category
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL,
        data={
            "account": other_account.pk,
            "category": expense_category.pk,
            "amount": "-12.50",
            "date": DATE,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "account" in response.data


def test_list_categories_unauthenticated_returns_403(api_client):
    response = api_client.get(URL_CATEGORY)

    assert response.status_code == 403


def test_list_categories_returns_only_current_user_categories(
    api_client,
    user,
    other_user,
):
    Category.objects.create(owner=user, name="school", type=Category.Type.EXPENSE)
    Category.objects.create(owner=other_user, name="School2", type=Category.Type.INCOME)

    api_client.force_authenticate(user=user)
    response = api_client.get(URL_CATEGORY)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "school"


def test_create_category_returns_201_and_sets_current_user_as_owner(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL_CATEGORY,
        data={"name": "School2", "type": "income"},
        format="json",
    )

    assert response.status_code == 201, response.data
    assert response.data["id"] is not None
    assert response.data["created_at"] is not None
    assert Category.objects.get(pk=response.data["id"]).owner == user
    assert Category.objects.filter(pk=response.data["id"]).exists()


def test_create_duplicate_category_returns_400(api_client, user):
    Category.objects.create(owner=user, name="School", type=Category.Type.INCOME)
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL_CATEGORY,
        data={"name": "School", "type": "income"},
        format="json",
    )

    assert response.status_code == 400, response.data
    assert "non_field_errors" in response.data
    assert Category.objects.filter(owner=user, name="School").count() == 1


def test_put_category_returns_405(api_client, user, expense_category):
    api_client.force_authenticate(user=user)

    response = api_client.put(
        category_url(expense_category.pk),
        data={"name": "Groceries", "type": "expense"},
        format="json",
    )

    assert response.status_code == 405, response.data


def test_retrieve_category_returns_200(api_client, user, expense_category):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        category_url(expense_category.pk),
    )

    assert response.status_code == 200, response.data
    assert response.data["name"] == expense_category.name


def test_retrieve_other_users_category_returns_404(
    api_client, user, other_expense_category
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        category_url(other_expense_category.pk),
    )

    assert response.status_code == 404, response.data


def test_patch_category_name_returns_200(api_client, user, expense_category):
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        category_url(expense_category.pk),
        data={"name": "Groceries"},
        format="json",
    )

    assert response.status_code == 200, response.data
    assert response.data["name"] == "Groceries"
    expense_category.refresh_from_db()
    assert expense_category.name == "Groceries"


def test_patch_category_type_with_transactions_returns_400(
    api_client, user, account, expense_category
):
    Transaction.objects.create(
        account=account,
        category=expense_category,
        amount=Decimal("-1.00"),
        date=datetime.date(2026, 11, 20),
    )
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        category_url(expense_category.pk),
        data={"type": "income"},
        format="json",
    )

    assert response.status_code == 400, response.data
    assert "type" in response.data
    expense_category.refresh_from_db()
    assert expense_category.type == "expense"


def test_delete_category_returns_204(api_client, user, expense_category):
    api_client.force_authenticate(user=user)
    pk = expense_category.pk
    response = api_client.delete(
        category_url(expense_category.pk),
    )
    assert response.status_code == 204, response.data
    assert not Category.objects.filter(pk=pk).exists()


def test_delete_category_with_transactions_returns_409(
    api_client, user, account, expense_category
):
    Transaction.objects.create(
        account=account,
        category=expense_category,
        amount=Decimal("-1.00"),
        date=datetime.date(2026, 11, 20),
    )
    api_client.force_authenticate(user=user)

    pk = expense_category.pk
    response = api_client.delete(
        category_url(expense_category.pk),
    )
    assert response.status_code == 409, response.data
    assert "transactions" in response.data["detail"], response.data
    assert Category.objects.filter(pk=pk).exists()


def test_delete_other_users_category_returns_404(
    api_client, user, other_expense_category
):
    api_client.force_authenticate(user=user)

    pk = other_expense_category.pk
    response = api_client.delete(
        category_url(other_expense_category.pk),
    )
    assert response.status_code == 404, response.data
    assert Category.objects.filter(pk=pk).exists()


def test_create_category_ignores_owner_in_payload(api_client, user, other_user):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        URL_CATEGORY,
        data={"owner": other_user.pk, "name": "School", "type": "income"},
        format="json",
    )

    assert response.status_code == 201, response.data
    assert Category.objects.filter(owner=user, name="School").count() == 1
