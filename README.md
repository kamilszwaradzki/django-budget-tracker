# Budget Tracker API

A REST API for managing personal finances, including accounts, income and expense categories, financial transactions, and monthly budgets.

## Project Status

**Active development.** I have a professional background in PHP (Symfony, Laravel). This is my first Django project: I'm learning the framework by building a finance app with real business rules. The design decisions below explain the trade-offs.

**Highlights:** service layer with keyword-only arguments · `Decimal` money · per-user data isolation · DB-level constraints · two-phase validation · domain errors mapped to HTTP 409 · 38 pytest tests

## Features & Roadmap

- [x] Project skeleton and Django configuration
- [x] Environment-based configuration and secret management
- [x] Custom User model
- [x] Account model with timestamp tracking
- [x] Category model with database-level uniqueness constraints
- [x] Django Admin configuration for core models
- [x] Transaction model
- [ ] Recurring transaction definitions
- [ ] Monthly budgets with `ok`, `warning`, and `over` spending statuses
- [ ] Idempotent generation of recurring transactions
- [x] Service layer for business logic (transactions and categories)
- [x] REST API: list and create transactions
- [x] REST API: full CRUD for categories (`PATCH` only, no `PUT`)
- [ ] REST API: retrieve, update and delete transactions, filtering and pagination
- [ ] REST API: accounts with derived balances
- [x] API root with links to all endpoints (`/` redirects to `/api/`)
- [x] Per-user data isolation (queryset filtering and protection against ID enumeration)
- [x] Global error handling (Django `ValidationError` → HTTP 400, domain errors → HTTP 409)
- [ ] JWT authentication and authorization
- [x] Automated tests (model, service and API tests for transactions and categories)
- [ ] PostgreSQL integration
- [ ] Docker configuration
- [ ] CI pipeline

## Tech Stack

- **Python 3.12+**: primary programming language
- **Django 6.1**: backend framework
- **Django REST Framework**: REST API layer
- **pytest + pytest-django**: tests
- **Ruff**: linting and formatting
- **SQLite**: development database
- **PostgreSQL**: planned database backend
- **python-dotenv**: environment variable management

## Getting Started

### Requirements

- Python 3.12+
- Git
- pip

### Installation

Clone the repository:

```bash
git clone https://github.com/kamilszwaradzki/django-budget-tracker.git
cd django-budget-tracker
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

If you are using Fish shell:

```fish
source .venv/bin/activate.fish
```

Install dependencies:

```bash
pip install -r requirements.txt
```

To develop the project and run tests, install `requirements-dev.txt`. It includes the production dependencies as well:

```bash
pip install -r requirements-dev.txt
```

Create your local environment configuration:

```bash
cp .env.example .env
```

Generate a Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set `SECRET_KEY` in `.env` to the generated value. Set `DEBUG=True` for local development.

Apply database migrations:

```bash
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

The application will be available at:

`http://127.0.0.1:8000/`

The Django Admin interface is available at:

`http://127.0.0.1:8000/admin/`

## API Endpoints

All endpoints except the API root require authentication. For local testing, log in through the browsable API at `/api-auth/login/` with the account created by `createsuperuser`.

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/` | API root with links to all endpoints (no login required) |
| `GET` | `/api/transactions/` | list the current user's transactions |
| `POST` | `/api/transactions/` | create a transaction |
| `GET` | `/api/categories/` | list the current user's categories |
| `POST` | `/api/categories/` | create a category |
| `GET` | `/api/categories/<id>/` | retrieve a category |
| `PATCH` | `/api/categories/<id>/` | update a category's name or type |
| `DELETE` | `/api/categories/<id>/` | delete a category |

Status codes used by the category endpoints:

- `400`: invalid data, a duplicate name and type, or a type change on a category that has transactions
- `404`: the category does not exist or belongs to another user
- `405`: `PUT` is not supported, use `PATCH`
- `409`: the category cannot be deleted because it has transactions

Errors that do not belong to a single field, such as a duplicate category, are returned under `non_field_errors`.

## Running Tests

```bash
pytest -v
```

The service tests check:

- transactions: income and expense amount rules, including a zero amount, and ownership of accounts and categories
- creating categories: duplicate name and type, a name made only of whitespace, and a duplicate that reaches the database (the `IntegrityError` safety net)
- updating categories: name changes, a rename to an existing name, and the type lock when transactions exist, including sending the same type again
- deleting categories: deletion without transactions, and `CategoryInUseError` with no data lost when transactions exist

The API tests check:

- authentication is required
- lists show only the current user's transactions and categories
- valid transactions and categories are created with a 201 response, and the owner is always the current user, even if the request sends another `owner`
- another user's account is rejected with a 400 response
- a duplicate category returns 400 with `non_field_errors`
- another user's category returns 404 for both `GET` and `DELETE`, and is not deleted
- `PATCH` renames a category, a type change with transactions returns 400, and `PUT` returns 405
- `DELETE` returns 204, or 409 with a message when the category has transactions

The model tests check:

- `full_clean()` enforces database constraints, such as the non-zero amount check

The root tests check:

- `/` redirects to the API root, which lists the endpoints without login

## Design Decisions

### Custom User Model

I created a custom User model at the start of the project. Changing the user model after the initial migrations can be difficult. This is why I made this decision early.

### Decimal Instead of Float

Financial values use Django's `DecimalField` instead of floating-point numbers. For example, in Python, `0.1 + 0.2` with floats produces `0.30000000000000004`. This can cause problems when working with money.

### Derived Account Balances

Account balances will be calculated from financial transactions. I decided not to add a separate `current_balance` field for now. This avoids keeping two versions of the same data in sync when transactions are created, updated, or deleted.

### Database-Level Constraints

Category uniqueness is enforced using Django's `UniqueConstraint`. A user cannot create two categories with the same name and type. Categories with the same name but different types are allowed. The database enforces this rule even when application-level validation is bypassed.

### `RESTRICT` on the Category Foreign Key

A category cannot be deleted while transactions still reference it. I used `on_delete=models.RESTRICT` instead of `CASCADE`, because silently removing historical transactions when a category is deleted would corrupt financial data. If a user wants to remove a category, they must first deal with the related transactions.

I chose `RESTRICT` instead of `PROTECT` because `PROTECT` also blocked deleting the whole user. With `RESTRICT`, deleting a user still works, because their transactions are deleted through the account `CASCADE` in the same operation. I checked both cases in the Django shell.

### Two-Phase Validation

Validation happens in two places, on purpose. The serializer checks the shape of the input: required fields, correct types, and whether the referenced account and category exist and belong to the current user. The service layer checks the business rules: an expense must have a negative amount, an income must have a positive amount, and the amount cannot be zero. This split keeps the HTTP layer thin. The same business rules can also be reused outside the API, for example in management commands or background jobs.

### Environment-Based Configuration

Sensitive settings, including the Django secret key, are loaded from environment variables. They are not hardcoded in the repository. If a required setting is missing, the application stops instead of using an insecure default.

### Separation of Business Logic

Business logic lives in a service layer (`budgets/services.py`), not in views or serializers. Creating a transaction goes through `create_transaction()`. The API view only passes validated data to it in `perform_create()`, so the view stays thin and has no business rules of its own.

The service functions use keyword-only arguments, for example `create_transaction(*, user, account, ...)`. Every call has to name its arguments, so it is not possible to accidentally swap `account` and `category` or two amounts.

The service raises Django's `ValidationError`, not the DRF one. This keeps the service independent of the API layer, so the same function can be used later in a management command or a background job. A custom DRF exception handler (`budgets/exceptions.py`) converts Django's `ValidationError` into an HTTP 400 response with field-level errors.

Before saving, the service calls `full_clean()` on the model. This runs model-level validation, including field validators and database constraints such as the non-zero amount check, so invalid data is rejected with a clear error before it reaches the database.

### Category Service

Categories follow the same pattern as transactions: `create_category()`, `update_category()` and `delete_category()` in the service layer, and thin views that only call them.

The name is stripped of leading and trailing whitespace before validation. A name made only of spaces becomes empty and is rejected by `full_clean()`, the same as an empty name. This also means that `"Food"` and `" Food "` cannot exist as two different categories.

`update_category()` takes optional `name` and `type` arguments, where `None` means "do not change". This matches `PATCH`, where DRF passes only the fields the client sent.

### Two Layers of Duplicate Protection

`full_clean()` checks the `UniqueConstraint` before saving and returns a clear validation error. This covers almost every case.

Two requests that arrive at the same time can both pass this check before either of them saves. The database then rejects the second one with an `IntegrityError`. The service catches it and raises the same `ValidationError` as `full_clean()`, so the client gets a 400 instead of a 500.

`save()` runs inside `transaction.atomic()`. This creates a savepoint, so after an `IntegrityError` the outer transaction can continue. Without it, every following query in the same transaction fails with `TransactionManagementError`. A test simulates the race by disabling `full_clean()`, so the duplicate reaches the database.

Limitation: every `IntegrityError` when saving a category is reported as a duplicate. This is correct today, because the unique constraint is the only constraint on this table. If another constraint is added, the error will need to be inspected.

### Category Type Is Locked Once It Has Transactions

The amount rule depends on the category type: an expense is negative, an income is positive. Changing the type of a category that already has transactions would make all of them break this rule. `update_category()` rejects such a change with a 400 error on the `type` field. Renaming is always allowed, and sending the current type again is not treated as a change.

The rule is checked before any field is assigned. If the update is rejected, the category object in memory still matches the database.

### Domain Exception Between the Service and HTTP

Deleting a category that has transactions raises `RestrictedError`, because of `on_delete=RESTRICT`. The service catches it and raises its own `CategoryInUseError` from `budgets/errors.py`. The exception handler converts it into an HTTP 409 Conflict.

This keeps each layer independent: the service does not know about HTTP status codes, and the view does not know about ORM exceptions.

I chose 409 instead of 400 because the request itself is valid. The operation is blocked by the current state of the data, not by wrong input.

`RestrictedError` is a subclass of `IntegrityError`, but I catch `RestrictedError` explicitly, so other integrity errors are not reported as "category in use". It is raised by Django's deletion collector in Python, before any `DELETE` query is sent, so the delete does not need `transaction.atomic()`.

### 404 Instead of 403 for Other Users' Resources

Views filter their querysets by the current user. A category that belongs to someone else is simply not found, and the API returns 404. A 403 would confirm that a resource with this ID exists, which makes it possible to discover other users' data by trying IDs.

### PATCH Only

The category detail endpoint allows `GET`, `PATCH` and `DELETE`, but not `PUT`. A category has only two editable fields, and `PATCH` covers every update. One way of updating means less code and fewer cases to test. `PUT` returns 405 Method Not Allowed.

### Error Format

Django puts errors that do not belong to a single field under the `__all__` key. The exception handler moves them to `non_field_errors`, which is the DRF convention. The key is taken from `api_settings.NON_FIELD_ERRORS_KEY`, so it follows the DRF settings.
