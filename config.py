import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# CSV and Google Drive
GOOGLE_DRIVE_URL = os.getenv("GOOGLE_DRIVE_URL")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

# API
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 10
MAX_LIMIT = 100

# Scheduler
SCHEDULER_INTERVAL_DAYS = 1

# Logging
LOG_FILE_NAME = "app.log"
LOG_FILE_MAX_BYTES = 2000000
LOG_FILE_BACKUP_COUNT = 5
