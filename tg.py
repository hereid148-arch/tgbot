import asyncio
import aiohttp
import urllib.parse
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8838895544:AAEW6rnTh7gzVz7xIqDwUdBUdpQEQ-bfh4Q"  # 👈 ЗАМЕНИТЕ НА ТОКЕН ОТ @BotFather

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ГЕНЕРАЦИЯ КАРТИНКИ ==========
async def generate_image(prompt: str) -> BytesIO | None:
    """Генерация изображения через Pollinations.ai (бесплатно, без ключа)"""
    async with aiohttp.ClientSession() as session:
        try:
            # Кодируем текст запроса для URL
            encoded_prompt = urllib.parse.quote(prompt)
            
            # Разные стили на выбор (раскомментируйте нужный)
            
            # Обычный вариант
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024"
            
            # Стиль аниме
            # url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=anime"
            
            # Без логотипа
            # url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
            
            async with session.get(url, timeout=60) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return BytesIO(image_data)
                else:
                    print(f"Ошибка API: {resp.status}")
                    return None
        except asyncio.TimeoutError:
            print("Таймаут при генерации")
            return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

# ========== КОМАНДЫ БОТА ==========
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🎨 <b>Бот генерации картинок через нейросеть</b>\n\n"
        "✨ <b>Как работает:</b>\n"
        "Просто отправь мне любое текстовое описание,\n"
        "и я сгенерирую картинку с помощью ИИ!\n\n"
        "📝 <b>Примеры запросов:</b>\n"
        "• кот в космосе\n"
        "• cyberpunk girl with neon hair\n"
        "• закат на море, масляная живопись\n"
        "• аниме девочка с синими волосами\n\n"
        "⏱ <i>Генерация занимает 15-30 секунд</i>\n\n"
        "Отправь /help для советов",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📖 <b>Советы для лучших результатов:</b>\n\n"
        "1️⃣ <b>Пишите на английском</b>\n"
        "   (нейросеть лучше понимает)\n\n"
        "2️⃣ <b>Добавляйте стиль</b>\n"
        "   realistic, anime, oil painting, cyberpunk, fantasy\n\n"
        "3️⃣ <b>Указывайте детали</b>\n"
        "   цвет, освещение, настроение\n\n"
        "🔍 <b>Примеры хороших запросов:</b>\n"
        "• <code>a cute cat wearing a spacesuit, cartoon style, 4k</code>\n"
        "• <code>beautiful fantasy landscape with mountains and waterfall, digital art, highly detailed</code>\n"
        "• <code>anime girl with blue hair and cat ears, studio ghibli style</code>\n"
        "• <code>cyberpunk city at night, neon lights, rain, reflections, 8k</code>\n\n"
        "🎨 Просто отправь текст и получи картинку!",
        parse_mode="HTML"
    )

@dp.message(Command("styles"))
async def styles(message: Message):
    await message.answer(
        "🎨 <b>Стили для генерации:</b>\n\n"
        "Добавьте эти слова в запрос для нужного эффекта:\n\n"
        "• <b>realistic</b> — фотореализм\n"
        "• <b>anime</b> — аниме стиль\n"
        "• <b>oil painting</b> — масляная живопись\n"
        "• <b>watercolor</b> — акварель\n"
        "• <b>cyberpunk</b> — киберпанк\n"
        "• <b>fantasy</b> — фэнтези\n"
        "• <b>cartoon</b> — мультяшный\n"
        "• <b>sketch</b> — набросок\n\n"
        "📝 <b>Пример:</b>\n"
        "<code>dragon flying over castle, fantasy, oil painting</code>",
        parse_mode="HTML"
    )

@dp.message()
async def generate_image_command(message: Message):
    prompt = message.text.strip()
    
    # Проверка длины запроса
    if len(prompt) < 3:
        await message.answer("❌ Слишком короткое описание. Напишите хотя бы 3 слова.")
        return
    
    # Отправляем статус "печатает/загружает"
    await bot.send_chat_action(message.chat.id, "upload_photo")
    
    # Отправляем сообщение о начале генерации
    status_message = await message.answer(
        f"🎨 <b>Генерирую картинку...</b>\n\n"
        f"📝 Запрос: <i>{prompt[:100]}</i>\n\n"
        f"⏳ Обычно это занимает 15-30 секунд",
        parse_mode="HTML"
    )
    
    # Генерируем изображение
    image_io = await generate_image(prompt)
    
    if image_io:
        # Отправляем полученное изображение
        image_io.seek(0)
        await message.answer_photo(
            photo=types.BufferedInputFile(image_io.getvalue(), filename="generated.png"),
            caption=f"✨ <b>Ваша картинка готова!</b>\n\n📝 {prompt[:200]}",
            parse_mode="HTML"
        )
        # Удаляем сообщение о статусе
        await status_message.delete()
    else:
        await status_message.edit_text(
            f"❌ <b>Не удалось сгенерировать картинку</b>\n\n"
            f"📝 Запрос: {prompt[:100]}\n\n"
            f"<b>Возможные причины:</b>\n"
            f"• Сервис временно перегружен\n"
            f"• Запрос слишком сложный\n"
            f"• Попробуйте переформулировать\n\n"
            f"<b>Совет:</b> Попробуйте более простой запрос или напишите на английском",
            parse_mode="HTML"
        )

# ========== ЗАПУСК БОТА ==========
async def main():
    print("=" * 50)
    print("🎨 БОТ ГЕНЕРАЦИИ КАРТИНОК ЗАПУЩЕН")
    print("🤖 Нейросеть: Pollinations.ai (бесплатно)")
    print("📝 Для генерации отправьте боту любое описание")
    print("=" * 50)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
