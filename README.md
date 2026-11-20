# Budget Tracker API

A REST API for managing personal finances, including accounts, income and expense categories, financial transactions, and monthly budgets.

## Project Status

**Work in Progress**

I have a professional background in PHP development, mainly with Symfony and Laravel. This is my first project built with Django. I am using it to learn the framework by building a personal finance application with real business rules.

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
- [x] Service layer for business logic (transactions)
- [x] REST API endpoints and serializers (list and create transactions)
- [x] Per-user data isolation (queryset filtering and protection against ID enumeration)
- [x] Global validation error handling (Django ValidationError → HTTP 400)
- [ ] JWT authentication and authorization
- [x] Automated tests (service and API tests for transactions)
- [ ] PostgreSQL integration
- [ ] Docker configuration
- [ ] CI pipeline

## Tech Stack

- **Python 3.12+**: primary programming language
- **Django 6.1**: backend framework
- **Django REST Framework**: REST API layer (in progress)
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
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

If you are using Fish shell:

```fish
source venv/bin/activate.fish
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

## Running Tests

```bash
pytest -v
```

The service tests check:

- income and expense amount rules, including a zero amount
- ownership of accounts and categories

The API tests check:

- authentication is required
- the list shows only the current user's transactions
- a valid transaction is created with a 201 response
- another user's account is rejected with a 400 response

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

I plan to add a service layer for business logic. It will keep this logic separate from HTTP views and serializers. Transaction processing, budget calculations, and recurring transaction generation will have their own place outside the API layer.
