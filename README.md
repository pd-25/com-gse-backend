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
```

## Running the app

Start the FastAPI app with Uvicorn:

```bash
uvicorn main:app --reload
```

Or, if you are using `uv`:

```bash
uv run uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/` in your browser.

## Available endpoints

- `GET /` — welcome message
- `GET /users/` — user route placeholder

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
