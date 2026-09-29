import os
from pathlib import Path
from dotenv import load_dotenv

# Loyihaning asosiy (ildiz) papkasi yo'li
BASE_DIR = Path(__file__).resolve().parent

# .env faylini yuklaymiz
load_dotenv(BASE_DIR / ".env")

# Telegram bot tokeni
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or BOT_TOKEN.strip() in ("", "your_bot_token_here", "YOUR_BOT_TOKEN_HERE"):
    BOT_TOKEN = None

# Ma'lumotlar bazasi yo'li
DB_PATH = BASE_DIR / "database.db"

# Data papkasi yo'llari
DATA_DIR = BASE_DIR / "data"
EXTENSIONS_FILE = DATA_DIR / "extensions.json"
DEVICES_FILE = DATA_DIR / "devices.json"
DICTIONARY_FILE = DATA_DIR / "dictionary.json"
QUESTIONS_FILE = DATA_DIR / "questions.json"
