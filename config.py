# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # lit .env si présent

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change_me")

# Vérifie rapidement que les variables essentielles existent en dev
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("⚠️  Attention: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquant dans .env")
