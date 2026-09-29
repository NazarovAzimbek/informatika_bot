from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards import get_main_menu_keyboard, get_back_keyboard
import database

router = Router(name="start_router")

START_TEXT = (
    "👋 <b>Assalomu alaykum!</b>\n\n"
    "Men — <b>Informatika yordamchi</b> botiman.\n\n"
    "Men sizga:\n"
    "🔢 <b>Sanoq sistemalari</b>\n"
    "💾 <b>Axborot birliklari</b>\n"
    "🔤 <b>ASCII</b>\n"
    "📁 <b>Fayl kengaytmalari</b>\n"
    "💻 <b>Kompyuter qurilmalari</b>\n"
    "🧠 <b>Testlar</b>\n"
    "📚 <b>Informatika terminlari</b>\n\n"
    "bo‘yicha yordam bera olaman.\n\n"
    "Kerakli bo‘limni tanlang 👇"
)

HELP_TEXT = (
    "📚 <b>BOTDAN FOYDALANISH</b>\n\n"
    "🔢 <b>Sanoq sistemalari</b> — 2, 8, 10, 16 sanoq sistemalari o'rtasida o'tkazish va tushuntirish.\n"
    "💾 <b>Axborot birliklari</b> — bit, Bayt, KB, MB, GB, TB, PB konvertori.\n"
    "🔤 <b>ASCII</b> — Belgilar va ularning kodlari.\n"
    "📁 <b>Fayl kengaytmalari</b> — Kengaytma yoki fayl nomi orqali qidirish.\n"
    "💻 <b>Kompyuter qurilmalari</b> — Qurilmalar haqida to'liq ma'lumot.\n"
    "🧠 <b>Mini test</b> — O'z bilimlaringizni sinash uchun testlar.\n"
    "📚 <b>Informatika lug‘ati</b> — Muhim terminlar va misollar.\n"
    "📊 <b>Statistika</b> — Yechilgan testlar va o'zlashtirish foizi (/stats).\n"
    "👥 <b>Foydalanuvchilar soni</b> — Botdan foydalanuvchilar soni (/users).\n\n"
    "💡 <i>Istalgan vaqtda /menu orqali asosiy menyuga qaytishingiz mumkin.</i>"
)

ABOUT_TEXT = (
    "ℹ️ <b>INFORMATIKA YORDAMCHI</b>\n\n"
    "Maktab o‘quvchilari uchun Informatika fanini o‘rganishga yordam beruvchi qulay Telegram bot.\n\n"
    "<b>Versiya:</b> 1.0\n"
    "<b>Yo'nalish:</b> Ta'limiy yordamchi\n"
    "<b>Kutubxona:</b> aiogram 3.x\n"
    "<b>Baza:</b> SQLite (aiosqlite)\n\n"
    "<i>Bot ta'limiy maqsadda ishlab chiqilgan.</i>"
)


async def get_stats_message_text(user_id: int, full_name: str) -> str:
    """Foydalanuvchi statistikasini shakllantirish"""
    stats = await database.get_user_stats(user_id)
    return (
        f"📊 <b>MENING NATIJALARIM</b>\n\n"
        f"👤 <b>O'quvchi:</b> {full_name}\n"
        f"🏁 <b>Yechilgan testlar soni:</b> {stats['quizzes_count']} ta\n"
        f"❓ <b>Jami savollar:</b> {stats['total_questions']} ta\n"
        f"✅ <b>To'g'ri javoblar:</b> {stats['correct_answers']} ta\n"
        f"📈 <b>O'rtacha o'zlashtirish:</b> {stats['avg_percentage']}%\n\n"
        f"💡 <i>Ko'proq test ishlab o'z natijangizni yaxshilab boring!</i>"
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    """/start komandasi - salomlashuv, ro'yxatga olish va asosiy menyu"""
    if message.from_user:
        await database.add_or_update_user(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )

    await message.answer(
        text=START_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """/menu komandasi - asosiy menyuni ochish"""
    await message.answer(
        text="📱 <b>Asosiy menyu:</b>\nKerakli bo'limni tanlang 👇",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """/help komandasi - botdan foydalanish yo'riqnomasi"""
    await message.answer(
        text=HELP_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    """/about komandasi - bot haqida ma'lumot"""
    await message.answer(
        text=ABOUT_TEXT,
        reply_markup=get_back_keyboard()
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """/stats komandasi - shaxsiy statistikani ko'rish"""
    user_id = message.from_user.id if message.from_user else 0
    full_name = message.from_user.full_name if message.from_user else "Foydalanuvchi"
    stats_text = await get_stats_message_text(user_id, full_name)
    await message.answer(
        text=stats_text,
        reply_markup=get_back_keyboard()
    )


@router.message(Command("users"))
async def cmd_users(message: Message):
    """/users komandasi - bot foydalanuvchilari soni va umumiy testlar sonini ko'rish"""
    stats = await database.get_global_stats()
    text = (
        f"👥 <b>BOT FOYDALANUVCHILARI STATISTIKASI</b>\n\n"
        f"👤 <b>Jami o‘quvchilar (foydalanuvchilar):</b> {stats['users_count']} ta\n"
        f"🏁 <b>Jami yechilgan testlar:</b> {stats['quizzes_count']} ta\n\n"
        f"🚀 <i>Har bir yangi foydalanuvchi /start bosganda ushbu hisoblagich avtomatik oshib boradi.</i>"
    )
    await message.answer(
        text=text,
        reply_markup=get_back_keyboard()
    )


@router.callback_query(F.data == "menu_stats")
async def cb_stats(call: CallbackQuery):
    """Statistika tugmasi bosilganda"""
    user_id = call.from_user.id
    full_name = call.from_user.full_name
    stats_text = await get_stats_message_text(user_id, full_name)
    await call.message.edit_text(
        text=stats_text,
        reply_markup=get_back_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "menu_main")
async def cb_main_menu(call: CallbackQuery):
    """Asosiy menyuga qaytish callback'i"""
    await call.message.edit_text(
        text=START_TEXT,
        reply_markup=get_main_menu_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "menu_about")
async def cb_about(call: CallbackQuery):
    """Bot haqida menyu tugmasi bosilganda"""
    await call.message.edit_text(
        text=ABOUT_TEXT,
        reply_markup=get_back_keyboard()
    )
    await call.answer()
