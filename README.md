# ecom-gse-backend

A FastAPI backend boilerplate for building e-commerce and general service engine (GSE) APIs using Python.

## Overview

This project is a starter backend built with FastAPI and WirePy. It includes:

- FastAPI application entrypoint in `main.py`
- API routing with `app/routes/base.py`
- User route scaffolding in `app/routes/v1/route_user.py`
- Environment-based configuration in `app/core/config.py`
- SQLAlchemy/Alembic database scaffolding under `app/database/` and `alembicmigration/`

## Features

- Root endpoint at `/`
- User API namespace at `/users`
- Configured project settings via `.env`
- Ready for database migration support with Alembic

## Requirements

- Python 3.13+
- `pip` or `poetry` environment

## Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd ecom-gse-backend
   ```

2. Install dependencies using your preferred Python tool:

   - With `pip`:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```

   - With `uv`:
     ```bash
     uv install
     ```

## Configuration

Create a `.env` file in the project root with any required secrets, for example:

```env
SECRET_KEY=your-secret-key
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret
RAZORPAY_PAYMENT_CURRENCY=INR
USD_TO_INR_RATE=83.00
```

Use Razorpay **Test Mode** credentials for local payment testing. Keep
`RAZORPAY_KEY_SECRET` on the backend only; the order API returns the public key
ID required by Razorpay Checkout. Catalog prices stored in USD are converted to
INR using `USD_TO_INR_RATE`, and the backend recalculates every order total from
database product prices.

## Running the app

Start the FastAPI app with Uvicorn:

```bash
uvicorn main:app --reload --port 8002
```

Or, if you are using `uv`:

```bash
uv run uvicorn main:app --reload --port 8002
```

Then open `http://127.0.0.1:8002/` in your browser. The companion frontend's
local environment is configured to use this port because port 8000 may be used
by another local service.

## Available endpoints

- `GET /` — welcome message
- `GET /api/v1/web/categories/` — category listing
- `GET /api/v1/web/catalog/products/` — searchable product catalog
- `GET /api/v1/web/footer/` — footer configuration and links
- `POST /api/v1/web/auth/register/` — customer registration
- `POST /api/v1/web/auth/login/` — customer login
- `POST /api/v1/web/auth/refresh-token/` — rotate authentication tokens
- `GET /api/v1/web/auth/me/` — authenticated customer profile
- `POST /api/v1/web/auth/logout/` — revoke the current access token
- `POST /api/v1/web/payments/orders/` — create a Razorpay order from cart items
- `POST /api/v1/web/payments/verify/` — verify payment and confirm the booking
- `GET /api/v1/web/payments/bookings/` — list the authenticated user's bookings

## Project structure

- `main.py` — app entrypoint
- `app/core/config.py` — application settings
- `app/routes/base.py` — root API router
- `app/routes/v1/route_user.py` — user routing scaffold
- `app/schemas/` — Pydantic schemas
- `app/services/` — business logic layer
- `app/database/` — database setup and base models
- `alembicmigration/` — Alembic migration configuration

## Notes

This repository is currently a boilerplate and includes starter routes and configuration. The database and user service implementation are placeholders and can be extended with SQLAlchemy models, repository logic, and authentication.
