import json
import os
import secrets
import string
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, executor, types

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [7577911409]
DATA_FILE = "users.json"

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
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

# === ТЕЛЕГРАМ-БОТ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)
    if user_id not in data["users"]:
        code = generate_code()
        data["users"][user_id] = {
            "username": message.from_user.username or f"user_{user_id}",
            "unique_code": code,
            "points": 0
        }
        save_data(data)
        await message.answer(
            f"✅ Добро пожаловать!\nВаш уникальный код: {code}\nБаллов: 0",
            parse_mode="Markdown"
        )
    else:
        user = data["users"][user_id]
        await message.answer(
            f"Вы уже зарегистрированы!\nКод: {user['unique_code']}\nБаллов: {user['points']}",
            parse_mode="Markdown"
        )

@dp.message_handler(commands=["me"])
async def cmd_me(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)
    if user_id in data["users"]:
        user = data["users"][user_id]
        await message.answer(
            f"🔹 Код: {user['unique_code']}\n🔹 Баллов: {user['points']}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Сначала напишите /start")

@dp.message_handler(commands=["add"])
async def cmd_add(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        _, code, amount = message.text.split()
        amount = int(amount)
    except:
        await message.answer("Использование: /add <код> <баллы>")
        return

    data = load_data()
    for uid, user in data["users"].items():
        if user["unique_code"] == code:
            user["points"] += amount
            save_data(data)
            await message.answer(
                f"✅ +{amount} баллов пользователю с кодом {code}.\nНовый баланс: {user['points']}"
            )
            return
    await message.answer("❌ Код не найден.")

@dp.message_handler(commands=["remove"])
async def cmd_remove(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        _, code, amount = message.text.split()
        amount = int(amount)
    except:
        await message.answer("Использование: /remove <код> <баллы>")
        return

    data = load_data()
    for uid, user in data["users"].items():
        if user["unique_code"] == code:
            user["points"] = max(0, user["points"] - amount)
            save_data(data)
            await message.answer(
                f"✅ −{amount} баллов у пользователя с кодом {code}.\nНовый баланс: {user['points']}"
            )
            return
    await message.answer("❌ Код не найден.")

# === МИНИ-ВЕБ-СЕРВЕР ДЛЯ RENDER ===
async def health_check(request):
    return web.Response(text="OK", content_type="text/plain")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8000)))
    await site.start()

# === ЗАПУСК ===
if name == "main":
    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())
    executor.start_polling(dp, skip_updates=True)
