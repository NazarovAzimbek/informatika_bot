import json
import os
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from keyboards import get_back_keyboard, get_cancel_keyboard

router = Router(name="file_extensions_router")


class FileExtStates(StatesGroup):
    waiting_for_extension = State()


def load_extensions() -> dict:
    """extensions.json faylidan ma'lumotlarni o'qish"""
    try:
        with open(config.EXTENSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


EXTENSIONS_DATA = load_extensions()


def find_extension_info(query: str) -> tuple[bool, str]:
    """
    Kiritilgan so'rovdan (.docx, docx, rasm.png va h.k.) kengaytmani ajratish va ma'lumot berish
    """
    clean = query.strip().lower()
    if not clean:
        return False, "❌ Kengaytma yoki fayl nomini kiriting!"

    # 1. Agar to'g'ridan-to'g'ri . bilan boshlangan bo'lsa (masalan: .docx)
    if clean.startswith(".") and clean.count(".") == 1:
        ext = clean
    # 2. Agar fayl nomi bo'lsa (masalan: rasm.png yoki doc.archive.zip)
    elif "." in clean:
        _, ext = os.path.splitext(clean)
    # 3. Agar nuqtasiz yozilgan bo'lsa (masalan: docx yoki png)
    else:
        ext = f".{clean}"

    if ext in EXTENSIONS_DATA:
        info = EXTENSIONS_DATA[ext]
        msg = (
            f"📁 <b>{info['nomi']} ({ext})</b>\n\n"
            f"📌 <b>Turi:</b> {info['turi']}\n"
            f"💻 <b>Dastur:</b> {info['dastur']}\n"
            f"🎯 <b>Vazifasi:</b> {info['vazifasi']}"
        )
        return True, msg
    else:
        msg = (
            f"❓ <b>{ext}</b> kengaytmasi mening bazamda hozircha mavjud emas.\n\n"
            f"<i>Bazamizda eng mashhur 26 ta (.docx, .xlsx, .pptx, .pdf, .png, .mp4, .zip, .py va boshqalar) kengaytmalar mavjud.</i>"
        )
        return False, msg


def get_extensions_menu_keyboard() -> InlineKeyboardMarkup:
    """Fayl kengaytmalari bo'limi menyusi"""
    keyboard = [
        [
            InlineKeyboardButton(text="📄 Hujjatlar (.docx, .pdf...)", callback_data="fext_cat_docs"),
            InlineKeyboardButton(text="🖼 Rasmlar (.png, .jpg...)", callback_data="fext_cat_images"),
        ],
        [
            InlineKeyboardButton(text="🎵 Media (.mp3, .mp4...)", callback_data="fext_cat_media"),
            InlineKeyboardButton(text="📦 Arxivlar (.zip, .rar...)", callback_data="fext_cat_archives"),
        ],
        [
            InlineKeyboardButton(text="💻 Kod va Dasturlar (.py, .exe...)", callback_data="fext_cat_code"),
        ],
        [
            InlineKeyboardButton(text="🔍 Kengaytmani qidirish", callback_data="fext_search"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_after_ext_keyboard() -> InlineKeyboardMarkup:
    """Qidiruvdan so'ng ko'rsatiladigan tugmalar"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔍 Boshqa kengaytma qidirish", callback_data="fext_search"),
            InlineKeyboardButton(text="📁 Kengaytmalar menyusi", callback_data="menu_file_ext"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "menu_file_ext")
async def cb_file_ext_menu(call: CallbackQuery, state: FSMContext):
    """Fayl kengaytmalari asosiy menyusi"""
    await state.clear()
    intro_text = (
        "📁 <b>Fayl kengaytmalari bo'limi</b>\n\n"
        "Fayl kengaytmasi uning qanday turdagi axborotni saqlashi va qaysi dasturda ochilishini bildiradi.\n\n"
        "Quyidagi toifalardan birini tanlang yoki to'g'ridan-to'g'ri kengaytma/fayl nomini "
        "(masalan: <code>.docx</code> yoki <code>rasm.png</code>) yozib yuboring:"
    )
    await call.message.edit_text(
        text=intro_text,
        reply_markup=get_extensions_menu_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "fext_search")
async def cb_search_ext_prompt(call: CallbackQuery, state: FSMContext):
    """Kengaytma nomini yozishni so'rash"""
    await state.set_state(FileExtStates.waiting_for_extension)
    await call.message.edit_text(
        text=(
            "🔍 <b>Fayl kengaytmasini qidirish</b>\n\n"
            "Kengaytmani yoki fayl nomini yozib yuboring:\n"
            "<i>(Misollar: <code>.docx</code>, <code>png</code>, <code>referat.pdf</code>, <code>kitob.epub</code>)</i>"
        ),
        reply_markup=get_cancel_keyboard("menu_file_ext")
    )
    await call.answer()


@router.callback_query(F.data.startswith("fext_cat_"))
async def cb_show_category(call: CallbackQuery):
    """Kategoriyalar bo'yicha tezkor ko'rish"""
    cat = call.data.replace("fext_cat_", "")

    cat_map = {
        "docs": ([".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".pdf", ".txt", ".csv"], "📄 <b>Hujjat va jadvallar</b>"),
        "images": ([".jpg", ".jpeg", ".png", ".gif"], "🖼 <b>Grafik tasvirlar (Rasmlar)</b>"),
        "media": ([".mp3", ".wav", ".mp4", ".avi", ".mkv"], "🎵 <b>Audio va Video fayllar</b>"),
        "archives": ([".zip", ".rar", ".7z"], "📦 <b>Siqilgan arxiv fayllar</b>"),
        "code": ([".exe", ".py", ".html", ".css", ".js"], "💻 <b>Dasturlar va Dasturlash kodlari</b>")
    }

    if cat not in cat_map:
        await call.answer()
        return

    ext_list, cat_title = cat_map[cat]
    lines = [f"{cat_title}\n"]

    for ext in ext_list:
        if ext in EXTENSIONS_DATA:
            info = EXTENSIONS_DATA[ext]
            lines.append(f"• <b>{ext}</b> — {info['turi']} <i>({info['dastur']})</i>")

    lines.append("\n💡 <i>To'liqroq ma'lumot olish uchun kengaytma nomini yuborishingiz mumkin.</i>")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📁 Bo'lim menyusi", callback_data="menu_file_ext")],
        [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")]
    ])

    await call.message.edit_text(
        text="\n".join(lines),
        reply_markup=kb
    )
    await call.answer()


@router.message(FileExtStates.waiting_for_extension)
async def process_extension_input(message: Message, state: FSMContext):
    """Kiritilgan kengaytmani qidirish"""
    await state.clear()
    _, res_text = find_extension_info(message.text)
    await message.answer(
        text=res_text,
        reply_markup=get_after_ext_keyboard()
    )
