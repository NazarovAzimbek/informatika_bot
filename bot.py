import asyncio
import io
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Windows konsolida UTF-8 (emojilar va o'zbekcha harflar) xatosiz chiqishi uchun
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import config
import database
from handlers import (
    start,
    number_systems,
    information_units,
    ascii_handler,
    file_extensions,
    computer_devices,
    quiz,
    dictionary,
    common
)

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("informatika_bot")


async def handle_health_check(request):
    """Render uchun Health Check (salomatlik tekshiruvi) sahifasi"""
    return web.Response(
        text="🤖 Informatika yordamchi boti faol ishlamoqda!",
        content_type="text/plain; charset=utf-8"
    )


async def start_web_server():
    """Render Web Service portini tinglovchi yengil server"""
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Veb-server {port}-portda muvaffaqiyatli ishga tushdi (Render uchun).")


async def main():
    # 1. Token borligini tekshiramiz
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi! .env faylini to'ldiring.")
        print("\n" + "=" * 60)
        print("❌ DIQQAT: BOT_TOKEN topilmadi!")
        print("Loyiha papkasidagi '.env' faylini oching va unga")
        print("BotFather bergan tokenni quyidagicha yozing:")
        print("BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
        print("=" * 60 + "\n")
        return

    # 2. SQLite ma'lumotlar bazasini ishga tushirish
    await database.init_db()

    # 3. Render Web Service uchun veb-serverni ishga tushirish
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Veb-serverni ishga tushirishda ogohlantirish: {e}")

    # 4. Bot va Dispatcher yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # 5. Routerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(number_systems.router)
    dp.include_router(information_units.router)
    dp.include_router(ascii_handler.router)
    dp.include_router(file_extensions.router)
    dp.include_router(computer_devices.router)
    dp.include_router(quiz.router)
    dp.include_router(dictionary.router)
    dp.include_router(common.router)  # Har doim oxirida bo'lishi kerak

    logger.info("🚀 Informatika yordamchi boti muvaffaqiyatli ishga tushmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
