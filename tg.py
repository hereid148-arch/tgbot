import os
import asyncio
import aiohttp
import urllib.parse
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from flask import Flask
import threading

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ Ошибка: BOT_TOKEN не найден в переменных окружения!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# ========== ГЕНЕРАЦИЯ КАРТИНОК ==========
async def generate_image(prompt: str) -> BytesIO | None:
    async with aiohttp.ClientSession() as session:
        try:
            encoded = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512"
            async with session.get(url, timeout=45) as resp:
                if resp.status == 200:
                    return BytesIO(await resp.read())
        except Exception as e:
            print(f"Ошибка: {e}")
    return None

# ========== КОМАНДЫ БОТА ==========
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🎨 <b>Бот генерации картинок</b>\n\n"
        "Просто отправь описание картинки!\n\n"
        "Примеры:\n"
        "• кот в космосе\n"
        "• cyberpunk city\n"
        "• аниме девушка",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📖 <b>Советы:</b>\n\n"
        "• Пишите на английском\n"
        "• Добавляйте стиль (realistic, anime)\n"
        "• Будьте конкретны\n\n"
        "Пример: <code>beautiful sunset ocean realistic</code>",
        parse_mode="HTML"
    )

@dp.message()
async def generate(message: Message):
    prompt = message.text.strip()
    
    if len(prompt) < 3:
        await message.answer("❌ Слишком короткое описание")
        return
    
    status = await message.answer(f"🎨 Генерирую: {prompt[:50]}...\n⏳ 15-30 секунд")
    
    image = await generate_image(prompt)
    
    if image:
        image.seek(0)
        await message.answer_photo(
            photo=types.BufferedInputFile(image.getvalue(), filename="image.png"),
            caption=f"✅ {prompt[:200]}"
        )
        await status.delete()
    else:
        await status.edit_text("❌ Ошибка. Попробуйте другой запрос.")

# ========== ЗАПУСК ==========
async def main():
    print("🤖 Бот запущен на Render!")
    print(f"✅ Токен загружен из переменной окружения")
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    asyncio.run(main())
