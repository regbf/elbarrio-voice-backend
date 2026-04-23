import gspread
from google.oauth2.service_account import Credentials
from app.config import GOOGLE_SHEETS_FILE, GOOGLE_CREDENTIALS_FILE
from datetime import datetime
import uuid
import json
import os

# Escopos necessários
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    # Lê o ficheiro JSON e cria credenciais com os escopos
    creds_path = os.path.join(os.path.dirname(__file__), '..', GOOGLE_CREDENTIALS_FILE)
    creds_path = os.path.abspath(creds_path)
    with open(creds_path, "r") as f:
        creds_info = json.load(f)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_client()
    workbook = client.open(GOOGLE_SHEETS_FILE)
    return workbook.worksheet(sheet_name)

# O resto do ficheiro permanece igual (ensure_sheet_exists, check_availability_sheets, etc.)