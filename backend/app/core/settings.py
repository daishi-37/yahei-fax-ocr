import os
from dotenv import load_dotenv

load_dotenv()

# Environment
BASE_PATH = str(os.getenv("BASE_PATH", "api"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))

# Gmail Settings
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GMAIL_IMAP_SERVER = os.getenv("GMAIL_IMAP_SERVER", "imap.gmail.com")
GMAIL_IMAP_PORT = int(os.getenv("GMAIL_IMAP_PORT", "993"))

# SMTP Settings (for future use)
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# X-API Settings (Mock)
X_API_URL = os.getenv("X_API_URL", "https://api.x.com/upload")
X_API_KEY = os.getenv("X_API_KEY")

# Dify Settings (Mock)
DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/ocr")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")

# Notion Settings
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# File Storage
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
EMAIL_STORAGE_PATH = f"{STORAGE_PATH}/emails"
PDF_STORAGE_PATH = f"{STORAGE_PATH}/pdfs"

# Polling Settings
EMAIL_POLLING_INTERVAL_MINUTES = int(os.getenv("EMAIL_POLLING_INTERVAL_MINUTES", "5"))
