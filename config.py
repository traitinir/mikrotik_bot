import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    ALLOWED_CHAT_IDS = [id.strip() for id in os.getenv('ALLOWED_CHAT_IDS', '').split(',') if id.strip()]
    
    MIKROTIK_HOST = os.getenv('MIKROTIK_HOST', '152.231.27.30')
    MIKROTIK_PORT = int(os.getenv('MIKROTIK_PORT', '8754'))
    MIKROTIK_USER = os.getenv('MIKROTIK_USER', '')
    MIKROTIK_PASS = os.getenv('MIKROTIK_PASS', '')