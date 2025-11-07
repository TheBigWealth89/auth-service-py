import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Async DB URL for asyncpg driver
DATABASE_URL = os.getenv("DATABASE_URL")
