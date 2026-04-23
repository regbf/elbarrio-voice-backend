import os
from dotenv import load_dotenv

load_dotenv()

USE_PROVIDER = os.getenv("USE_PROVIDER", "sheets")
DEFAULT_RESTAURANT_ID = os.getenv("DEFAULT_RESTAURANT_ID", "elbarrio")
GOOGLE_SHEETS_FILE = os.getenv("GOOGLE_SHEETS_FILE", "ElBarrioPilot")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")