import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
client = gspread.authorize(creds)

# Tenta abrir a sheet pelo nome
sheet = client.open('ElBarrioPilot')
print('✅ Sheet encontrada:', sheet.title)