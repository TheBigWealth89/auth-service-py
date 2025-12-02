import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Async DB URL for asyncpg driver
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY_REFRESH = os.getenv("SECRET_KEY_REFRESH")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)

EMAIL = os.getenv("EMAIL", "")
if not EMAIL:
    raise ValueError("EMAIL environment variable is not set")
# Resend API Key
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
