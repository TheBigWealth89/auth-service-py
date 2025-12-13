# 🛡️ FastAPI Robust Authentication Service

A high-performance, secure, and production-ready authentication microservice built with **FastAPI** and **Python**. Designed with **SOLID principles**, strict typing, and industry-standard security practices including Opaque Refresh Tokens, Reuse Detection, and HttpOnly Cookies.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)
![Security](https://img.shields.io/badge/Security-OWASP%20Compliant-red)
![License](https://img.shields.io/badge/License-MIT-green)

# 🛡️ FastAPI Authentication Service

A secure, production-ready authentication microservice built with **FastAPI** and **Python**. Designed with clear abstractions, strong typing, and modern security practices (opaque refresh tokens, reuse detection, HttpOnly cookies).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg) ![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Run the Server](#run-the-server)
- [API Endpoints (quick)](#api-endpoints-quick)
- [Testing](#testing)
- [Development Notes](#development-notes)
- [Contributing](#contributing)
- [License](#license)

## Overview

This service handles user lifecycle tasks: registration, email verification, login, token rotation, social login (Google), and secure session management. It pairs stateless access tokens (JWT) with stateful opaque refresh tokens to enable secure token rotation and reuse detection.

## Features

- Hybrid auth: short-lived JWT access tokens + DB-backed opaque refresh tokens
- Refresh token single-use + reuse detection (invalidates token family on suspicious reuse)
- HttpOnly cookies for tokens to reduce XSS risk
- Email verification with rate-limited resends (60s cooldown)
- Argon2 password hashing via `argon2-cffi`
- Async DB access with SQLAlchemy 2.0 + `asyncpg`
- Clear domain/service/repository separation using ABCs for testability

## Folder Structure

Below is the main project layout (top-level):

```
alembic.ini
alembic/
app/
  __init__.py
  main.py
  api/
    v1/
      auth_routes.py
      user_routes.py
      dependencies/
  core/
    config.py
    db.py
    mailer.py
    token.py
  domain/
    abstracts/
    auth/
    users/
  models/
  repositories/
  schema/
  test/
  utils/
requirements.txt
README.md
```

This matches the current repository. Expand as needed for new modules.

## Prerequisites

- Python 3.10+ installed
- PostgreSQL database
- `virtualenv` or `venv` for isolating dependencies

## Getting Started

1. Clone the repo:

```bash
git clone https://github.com/yourusername/auth-service.git
cd auth-service
```

2. Create and activate a virtual environment

On macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root with the variables your environment needs. Example:

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Secrets
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (Resend)
RESEND_API_KEY=re_123456789

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
```

Load these with your preferred method (e.g., `python-dotenv` used in `core/config.py`).

## Database Migrations

This project uses Alembic for migrations. To run migrations:

```bash
alembic upgrade head
```

When you add or change models, generate a migration:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Run the Server

Start the FastAPI app locally with Uvicorn:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

## API Endpoints (quick)

Authentication endpoints (main ones):

- `POST /auth/signup` — register a new user
- `POST /auth/login` — login, returns HttpOnly cookies
- `POST /auth/refresh` — rotate tokens (refresh)
- `POST /auth/logout` — invalidate session and clear cookies
- `GET /auth/google/login` — start Google OAuth flow

Verification endpoints:

- `POST /verify-email` — verify user account and optionally auto-login
- `POST /resend-verification` — resend verification email (rate limited)

Note: Check `app/api/v1/` for full route definitions and parameter details.

## Testing

Run tests with `pytest`:

```bash
pytest -q
```

Unit tests live under `app/test/`.

## Development Notes

- Password hashing: see `app/utils/password_hasher.py` (Argon2)
- Token logic: `app/domain/auth/token_service.py` and `app/core/token.py`
- Repositories implement abstract interfaces in `app/domain/abstracts/`

When adding features, prefer adding tests and migrations, and keep service logic separate from I/O.

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Describe feature"`
4. Push and open a PR

Please follow existing code style and add tests for new behavior.

## License

This project is provided under the MIT License. See the `LICENSE` file for details.

## Need help or want improvements?

Open an issue or contact the maintainer.
