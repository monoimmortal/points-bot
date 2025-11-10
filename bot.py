import json
import os
import secrets
import string
from aiogram import Bot, Dispatcher, executor, types

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [7577911409]
DATA_FILE = "users.json"

def generate_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    data = load_data()
    user
