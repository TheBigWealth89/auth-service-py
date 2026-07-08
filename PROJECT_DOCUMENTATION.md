# FastAPI Authentication Service - Full Exhaustive Project Documentation

## 1. Introduction and Overview
This document provides an exhaustive, component-by-component breakdown of the FastAPI Authentication Service. It is a production-ready authentication microservice built using Python 3.10+, FastAPI, and PostgreSQL. The application is designed strictly following **SOLID principles**, **Clean Architecture**, and **Domain-Driven Design (DDD)**. It uses **stateless JWTs** for access tokens and **stateful, opaque, database-backed refresh tokens** to implement a robust and secure session rotation mechanism.

---

## 2. Technology Stack
*   **Web Framework:** FastAPI (v0.121.0)
*   **ASGI Server:** Uvicorn (v0.38.0)
*   **Language:** Python 3.10+l
*   **Database:** PostgreSQL (via asyncpg)
*   **ORM:** SQLAlchemy 2.0 (Async)
*   **Migrations:** Alembic
*   **Password Hashing:** Argon2 (via argon2-cffi)
*   **Email Delivery:** Resend API
*   **Authentication mechanism:** Hybrid (Short-lived JWT Access Tokens + Opaque Refresh Tokens)
*   **OAuth:** Google OAuth2 (via google-auth)
*   **Data Validation:** Pydantic (v2)

---

## 3. Directory Structure
```text
auth-service-py/
├── alembic/                  # Alembic migration environment
│   ├── env.py                # Alembic environment configuration
│   ├── script.py.mako        # Template for migration files
│   └── versions/             # Migration scripts
├── alembic.ini               # Alembic config file
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application initialization & router inclusions
│   ├── api/
│   │   └── v1/
│   │       ├── auth_routes.py        # Login, refresh, logout endpoints
│   │       ├── user_routes.py        # Register, verify email, password reset, google auth
│   │       └── dependencies/         # FastAPI Dependency Injection
│   │           ├── get_refresh_token_repo.py
│   │           ├── get_user_repo.py
│   │           └── get_verification.py
│   ├── core/
│   │   ├── config.py         # Environment variables configuration loader
│   │   ├── db.py             # SQLAlchemy Async Engine and Session definition
│   │   ├── mailer.py         # ResendMailer implementation
│   │   └── token.py          # JWT creation and decoding logic
│   ├── domain/
│   │   ├── abstracts/        # Abstract Base Classes (ABCs) defining interfaces
│   │   │   ├── email_verify_abstract.py
│   │   │   ├── password_hasher_abstract.py
│   │   │   ├── password_reset_abstract.py
│   │   │   ├── refresh_token_abstract.py
│   │   │   └── user_abstract.py
│   │   ├── auth/             # Authentication core business logic
│   │   │   ├── auth_service.py
│   │   │   └── token_service.py
│   │   └── users/            # User lifecycle business logic
│   │       ├── email_verification_service.py
│   │       ├── google_oauth_service.py
│   │       ├── password_reset_service.py
│   │       └── user_service.py
│   ├── models/               # SQLAlchemy ORM Data Models
│   │   ├── email_verification_model.py
│   │   ├── password_reset_tokens.py
│   │   ├── refresh_token_model.py
│   │   └── user_model.py
│   ├── repositories/         # Concrete implementations of the ABCs
│   │   └── postgreSQL/
│   │       ├── email_verify_tokens_repo.py
│   │       ├── password_reset_repo.py
│   │       ├── refresh_token_repo.py
│   │       └── user_repo_postgres.py
│   ├── schema/               # Pydantic Data Transfer Objects (DTOs)
│   │   ├── auth_dto.py
│   │   └── user_dto.py
│   ├── test/                 # Pytest test suites
│   │   ├── test_db.py
│   │   └── test_refresh.py
│   └── utils/                # General utilities
│       └── password_hasher.py # Argon2 password hasher wrapper
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Database Schema (SQLAlchemy Models)

### `User` (`app/models/user_model.py`)
*   `id`: UUID (Primary Key, indexed, auto-generated)
*   `google_id`: String (Nullable)
*   `name`: String(150) (Not Null)
*   `email`: String(255) (Unique, Indexed, Not Null)
*   `hashed_password`: String(255) (Not Null)
*   `role`: String(50) (Default: "user", Not Null)
*   `provider`: String (Default: "local")
*   `is_verified`: Boolean (Default: False, Not Null)
*   `created_at`: DateTime(timezone=True) (Server default: `func.now()`, Not Null)

### `RefreshToken` (`app/models/refresh_token_model.py`)
*   `id`: String(64) (Primary Key, token_id UUID hex)
*   `user_id`: UUID (Foreign Key to `users.id`, Not Null)
*   `token_hash`: String(512) (Hashed opaque token secret, Not Null)
*   `revoked`: Boolean (Default: False, Not Null)
*   `created_at`: DateTime(timezone=True) (Server default: `func.now()`)
*   `expires_at`: DateTime(timezone=True) (Not Null)

### `EmailVerificationToken` (`app/models/email_verification_model.py`)
*   `id`: String(64) (Primary Key, token_id UUID hex)
*   `user_id`: UUID (Foreign Key to `users.id`, Unique, Not Null)
*   `hashed_token`: String(255) (Hashed token secret, Not Null)
*   `last_email_sent_at`: DateTime(timezone=True) (Nullable)
*   `expires_at`: DateTime(timezone=True) (Not Null)
*   `created_at`: DateTime(timezone=True) (Server default: `func.now()`, Not Null)

### `PasswordResetToken` (`app/models/password_reset_tokens.py`)
*   `id`: String(64) (Primary Key, token_id UUID hex)
*   `user_id`: UUID (Foreign Key to `users.id`, Unique, Not Null)
*   `hashed_token`: String(255) (Hashed token secret, Not Null)
*   `last_email_sent_at`: DateTime(timezone=True) (Nullable)
*   `expires_at`: DateTime(timezone=True) (Not Null)
*   `created_at`: DateTime(timezone=True) (Server default: `func.now()`, Not Null)

---

## 5. Schemas (Pydantic DTOs)

### Authentication DTOs (`app/schema/auth_dto.py`)
*   `LoginDTO`: 
    *   `email` (EmailStr)
    *   `password` (str, min_length=8)
*   `loginResponseDTO`:
    *   `access_token` (str)
*   `TokenDTO`:
    *   `access_token` (str)
    *   `refresh_token_raw` (str)
    *   `expires_at` (datetime)
    *   `token_type` (str, default="bearer")

### User DTOs (`app/schema/user_dto.py`)
*   `UserCreateDTO`:
    *   `name` (str, min_length=1)
    *   `email` (EmailStr)
    *   `password` (str, min_length=8)
*   `UserReadDTO` (Configured for ORM loading `from_attributes=True`):
    *   `id` (UUID)
    *   `name` (str)
    *   `email` (EmailStr)
    *   `created_at` (Optional[datetime])
*   `ResetPasswordDTO`:
    *   `email` (EmailStr)
*   `NewPasswordDTO`:
    *   `new_password` (str, min_length=8)

---

## 6. Abstract Interfaces (Domain Layer)
The application defines strict abstract contracts ensuring dependency inversion.

### `IUserRepository`
*   `get_user_by_email(email: str) -> Optional[User]`
*   `get_user_by_id(user_id: str) -> Optional[User]`
*   `create_user(user_create: UserCreateDTO, password_hash: str) -> User`
*   `mark_verified(user_id: int) -> Optional[User]`
*   `create_google_user(email: str, google_id: str, name: str) -> User`
*   `update_password(user_id: int, hashed_password: str)` *(Implicitly expected)*

### `PasswordHasher`
*   `hash(plain: str) -> str`
*   `verify(hashed: str, plain: str) -> bool`

### `IOpaqueRefreshToken`
*   `save_refresh_token(token_id: str, user_id: int, token_hash: str, expires_at: datetime) -> str`
*   `get_refresh_token_by_id(token_id: str) -> str`
*   `revoke_refresh_token(token_id: str)`
*   `revoke_all_refresh_tokens_for_user(user_id: int)`

### `IEmailRepository`
*   `create_token(token_id: str, user_id: int, token: str, expires_at: datetime) -> EmailVerificationToken`
*   `get_token_by_id(user_id: int) -> str`
*   `get_last_email_sent_at(user_id: int) -> Optional[datetime]`
*   `update_last_email_sent_at(user_id: int, timestamp: datetime)`
*   `delete_token(token_id: str) -> str`

### `IPasswordResetToken`
*   Identical method signatures to `IEmailRepository`, but interacts with `PasswordResetToken` entities.

---

## 7. PostgreSQL Repositories (Data Access Layer)

All repositories are initialized with an `async_session_factory`. They use `session.begin()` for all database operations, which automatically commits on success and rolls back on any exception — eliminating manual `try/except/rollback` boilerplate and preventing connection leaks.

### `PostgresUserRepository`
Implements `IUserRepository`. All write methods use `session.begin()`. `IntegrityError` (e.g. duplicate email) bubbles up naturally from within the transaction block and is handled by the domain layer. `session.refresh()` is called after the `begin()` block closes to reload DB-generated fields (IDs, timestamps) from the committed state.
### `PostgresRefreshTokenRepository`
Implements `IOpaqueRefreshToken`. Uses `session.begin()` for all saves and revocations. `revoke_all_refresh_tokens_for_user` fetches all active tokens and bulk-marks them within a single atomic transaction.
### `EmailVerifyTokensRepo`
Implements `IEmailRepository`. Has an upsert-style `create_token` that either updates an existing `EmailVerificationToken` row or creates a new one, entirely within a single `session.begin()` block.
### `PasswordResetTokenRepo`
Implements `IPasswordResetToken`. Identical pattern to `EmailVerifyTokensRepo` but for `PasswordResetToken` entities.

---

## 8. Domain Services (Business Logic)

### `AuthService` (`app/domain/auth/auth_service.py`)
*   `login(dto: LoginDTO)`: Validates email exists, checks if `user.is_verified`. Verifies password against hash. On success, utilizes `create_access_token` for the JWT and `TokenService._issue_refresh_token` to generate the opaque refresh token.
*   `logout(user_id: int)`: Proxies to repository to revoke all refresh tokens for the given user.

### `TokenService` (`app/domain/auth/token_service.py`)
*   `_issue_refresh_token(user_id)`: Generates a new `token_id` (uuid4) and a `secret` (64 bytes). Hashes the `secret` using Argon2. Saves the `token_hash` in the database. Returns raw `token_id.secret`.
*   `refresh_access_token(raw_token: str)`: 
    *   Splits the incoming token into `token_id` and `secret`.
    *   Fetches from database. If it does not exist, triggers a complete session invalidation (suspicious activity).
    *   If it is marked `revoked`, it signifies **Token Reuse**. It revokes *all* active tokens for the user and denies access.
    *   Validates expiry.
    *   Verifies the secret hash. If invalid, revokes the token.
    *   If fully valid, it immediately revokes the current token (Rotation), issues a new refresh token, and issues a new access token.

### `UserService` (`app/domain/users/user_service.py`)
*   `register(dto: UserCreateDTO)`: Uses a single `if/elif/else` decision tree to check for existing users. If the user exists and is **not** verified, it resends the verification email. If the user exists and **is** verified, it raises an error. Otherwise, it hashes the password, creates the user in the DB, and dispatches a verification email.

### `EmailVerificationService` (`app/domain/users/email_verification_service.py`)
*   `create_and_send_token(user)`: Enforces a 60-second rate limit using the `last_email_sent_at` column. Generates `token_id` and `secret`, hashes it, stores it with a 10-minute expiry, and triggers the Resend API.
*   `verify_token(raw_token: str)`: Validates the token string, checks database existence, checks expiry, verifies the secret hash. Discards the token after successful verification.

### `PasswordResetService` (`app/domain/users/password_reset_service.py`)
*   `create_and_send_token(dto: ResetPasswordDTO)`: Similar to email verification. Returns an opaque success message even if the user does not exist (prevents email enumeration). Enforces a 60-second rate limit. Sends an email.
*   `verify_token(raw_token: str)`: Standard token validation and cleanup logic.
*   `reset_password(raw_token: str, dto: NewPasswordDTO, user_repo)`: First runs `verify_token()`. If successful, hashes the new password and persists it using the user repository.

### `GoogleAuthService` (`app/domain/users/google_oauth_service.py`)
*   `login_with_google(google_id_token)`: Verifies the OAuth2 ID Token using Google's library. If the email is not found, dynamically creates an OAuth-based user account (bypassing password and automatically setting `is_verified=True`). Issues access and refresh tokens.

---

## 9. API Endpoints (`app/api/v1`)

### `auth_routes.py`
1.  **`POST /auth/login`**: Accepts `LoginDTO`. Sets an `HttpOnly`, `secure=False` (for local dev, should be `True` in production), `samesite="none"` cookie containing the raw refresh token, scoped to `path="/auth/refresh"`. Returns `{ "access_token": ... }`.
2.  **`POST /auth/refresh`**: Extracts `refresh_token` from cookies. Invokes `TokenService.refresh_access_token()`. Rotates the `refresh_token` cookie with the new value. Returns `{ "access_token": ..., "expires_at": ... }`.
3.  **`POST /auth/logout`**: Authenticated via JWT (`Depends(get_current_user_id)`). Calls `AuthService.logout()` which invalidates all tokens in the DB. Executes `response.delete_cookie("refresh_token")`.

### `user_routes.py`
1.  **`POST /auth/register`**: Accepts `UserCreateDTO`. Calls `UserService.register()`.
2.  **`GET /auth/verify-email`**: Accepts `token` as a query parameter. Marks user as verified, immediately logs them in by setting the `refresh_token` cookie and returning an `access_token`.
3.  **`POST /auth/google`**: Accepts `token` (Google ID token). Authenticates/Registers user, sets the `refresh_token` cookie, returns the `access_token` and user profile.
4.  **`POST /auth/reset-password`**: Accepts `ResetPasswordDTO`. Dispatches reset email.
5.  **`POST /auth/reset-password/confirm`**: Accepts `token` (query string) and `NewPasswordDTO` (body). Resets the user's password.

---

## 10. Dependency Injection (`app/api/v1/dependencies`)
The FastAPI route definitions rely on `Depends()` to inject concrete implementations, strictly satisfying the ABCs required by the Domain layer:
*   `get_user_repo()` -> `PostgresUserRepository`
*   `get_hasher()` -> `Argon2PasswordHasher`
*   `get_pw_reset_repo()` -> `PasswordResetTokenRepo`
*   `get_refresh_tokens_repo()` -> `PostgresRefreshTokenRepository`
*   `get_verification_repo()` -> `EmailVerifyTokensRepo`
*   `get_mailer()` -> `ResendMailer`
*   `enforce_login_rate_limit()` -> `RateLimitService` (Redis-backed, runs before login handler)
*(All repositories are initialized using the `AsyncSessionLocal` sessionmaker.)*

---

## 11. Core Implementations & Utilities

### `Argon2PasswordHasher` (`app/utils/password_hasher.py`)
Wraps `argon2-cffi`. Uses Python's `asyncio.get_running_loop().run_in_executor(None, ...)` to perform computationally heavy hashing and verification operations off the main async event loop.

### JWT Handling (`app/core/token.py`)
*   `create_access_token`: Generates a short-lived JWT using the standard `jose` library (Algorithm: HS256).
*   `get_current_user_id`: Dependency used on protected routes. Retrieves the JWT from the `Authorization: Bearer <token>` header, decodes it, and extracts the `sub` (user_id).

### Mailer (`app/core/mailer.py`)
*   `ResendMailer`: Wrapper around the `resend` python package. Exposes `send_verification_email` and `send_reset_password_email` using predefined HTML templates and deep-links back to the application.

### Configuration (`app/core/config.py`)
Loads settings via `python-dotenv`:
*   `DATABASE_URL`, `SECRET_KEY`, `SECRET_KEY_REFRESH`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `RESEND_API_KEY`, `GOOGLE_CLIENT_ID`.

### Database Connection (`app/core/db.py`)
Establishes the SQLAlchemy `create_async_engine` and `sessionmaker` (`AsyncSessionLocal`) with `expire_on_commit=False` and `autoflush=False`.

---

## 12. Database Queries & SQLAlchemy 2.0 Patterns

This project relies entirely on **SQLAlchemy 2.0** in **Async** mode (via `asyncpg`). It avoids legacy `session.query()` syntax in favor of the modern `select()` construct.

### 12.1. Async Session Management with `session.begin()`
All repository methods use a nested `session.begin()` context manager. This pattern automatically commits the transaction on clean exit and rolls back on any exception, eliminating manual `try/except/rollback` boilerplate and preventing connection leaks:
```python
async with self._session_factory() as session:
    async with session.begin():
        # ALL reads and writes happen here.
        # No manual commit() or rollback() ever needed.
```
`session.refresh(obj)` is called *after* the `begin()` block closes when DB-generated fields (e.g., auto-assigned IDs or server-default timestamps) need to be reloaded from the committed state.

### 12.2. Selecting Data (`select()`)
Queries are built using the `select()` statement and executed via `session.execute()`:
```python
stmt = select(User).where(User.email == email)
result = await session.execute(stmt)
user = result.scalars().first()  # returns the User ORM object or None
```
*   `result.scalars().first()`: Used when we expect zero or one result.
*   `result.scalar_one_or_none()`: Used for unique fetches where multiple results indicate a data integrity error.
*   `result.scalars().all()`: Used when fetching a list (e.g., all active refresh tokens for a user).

### 12.3. Direct Entity Lookups
For primary key lookups, `session.get()` is preferred as SQLAlchemy can serve it from the identity map without a round-trip to the database:
```python
return await session.get(RefreshToken, token_id)
```

### 12.4. Inserts
Objects are added to the session inside the `begin()` block. Any `IntegrityError` (e.g., a duplicate email) bubbles up naturally, triggering an automatic rollback:
```python
async with session.begin():
    session.add(new_user)
# Refresh after the transaction closes to get DB-assigned fields
await session.refresh(new_user)
```

### 12.5. Updates
Updates are performed by fetching the ORM object and mutating its attributes inside the `begin()` block. SQLAlchemy tracks the change and flushes it automatically on commit:
```python
async with session.begin():
    rt = await session.get(RefreshToken, token_id)
    if rt:
        rt.revoked = True
# Transaction auto-commits here
```

---

## 13. Security Deep Dive

1. **Password Hashing:** Argon2id is used as the current state-of-the-art recommendation by OWASP, mitigating brute-force and GPU-based dictionary attacks.
2. **Refresh Token Reuse Detection:** When a refresh token is rotated, the old one is marked as revoked rather than deleted. If a malicious actor steals the old refresh token and tries to use it, the `TokenService` detects this and revokes the **entire token family** for the user, effectively locking the attacker out.
3. **Opaque Tokens in Database:** Refresh tokens, verification tokens, and reset tokens are essentially passwords. They are constructed of `token_id.secret`. Only the `token_id` and the **hash** of the `secret` are stored in the database. If the database is compromised, the tokens cannot be used to forge sessions.
4. **HttpOnly Cookies:** Protecting the `refresh_token` from being read by JavaScript prevents Cross-Site Scripting (XSS) from compromising the persistent session.
5. **Anti-Enumeration:** The password reset flow returns a generic response whether an email exists or not.
6. **Rate Limiting:** Implementing a hard 60-second limit on outbound emails to prevent malicious spamming.
7. **Threadpool Execution:** Argon2 hashing is intentionally CPU intensive. Pushing this to an executor prevents the asynchronous event loop from blocking, maintaining high concurrency for FastAPI.

---

## 14. Setup and Execution

1.  **Environment:** Ensure Python 3.10+ and a PostgreSQL server.
2.  **Dependencies:** `pip install -r requirements.txt`
3.  **Env file:** Copy `.env.example` to `.env` and provide a valid asyncpg `DATABASE_URL` (e.g., `postgresql+asyncpg://user:password@localhost/dbname`).
4.  **Database Migration:** Execute `alembic upgrade head` to generate tables.
5.  **Execution:** Run `uvicorn app.main:app --reload`.
6.  **Testing:** Execute `pytest -q` which automatically drops into the test environment via `app/test/test_db.py` and `test_refresh.py`.
