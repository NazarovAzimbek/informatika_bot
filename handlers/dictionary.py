import json
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from keyboards import get_back_keyboard, get_cancel_keyboard

router = Router(name="dictionary_router")


class DictionaryStates(StatesGroup):
    waiting_for_term = State()


def load_dictionary() -> dict:
    """dictionary.json faylidan terminlarni o'qish"""
    try:
        with open(config.DICTIONARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


DICTIONARY_DATA = load_dictionary()


def format_term_card(term_key: str) -> str:
    """Termin haqida to'liq kartochka matni"""
    if term_key not in DICTIONARY_DATA:
        return "❓ Termin topilmadi."

    item = DICTIONARY_DATA[term_key]
    return (
        f"📚 <b>{item['termin'].upper()}</b>\n\n"
        f"📖 <b>Ta'rif:</b>\n{item['tarif']}\n\n"
        f"💡 <b>Misol:</b>\n{item['misol']}"
    )


def find_terms_by_query(query: str) -> list[str]:
    """Qidiruv so'rovi bo'yicha mos termin kalitlarini topish"""
    clean = query.strip().lower()
    if not clean:
        return []

    # 1. Aniq moslik
    if clean in DICTIONARY_DATA:
        return [clean]

    # 2. Boshlanishi yoki ichida kelishi
    matches = []
    for k, item in DICTIONARY_DATA.items():
        if clean in k or clean in item["termin"].lower():
            matches.append(k)

    # 3. Ta'rif ichida kelishi
    if not matches:
        for k, item in DICTIONARY_DATA.items():
            if clean in item["tarif"].lower():
                matches.append(k)

    return matches


def get_dictionary_menu_keyboard() -> InlineKeyboardMarkup:
    """Lug'at bo'limi asosiy menyusi"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔍 Termin qidirish", callback_data="dict_search_prompt"),
            InlineKeyboardButton(text="🎲 Tasodifiy termin", callback_data="dict_random"),
        ],
        [
            InlineKeyboardButton(text="📋 Barcha terminlar ro'yxati", callback_data="dict_list_page_0"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_terms_list_keyboard(page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    """Terminlar ro'yxatini sahifalab (pagination) chiqarish"""
    all_keys = sorted(list(DICTIONARY_DATA.keys()))
    total = len(all_keys)
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total)

    page_keys = all_keys[start_idx:end_idx]

    keyboard = []
    row = []
    for k in page_keys:
        title = DICTIONARY_DATA[k]["termin"].split(" (")[0]
        row.append(InlineKeyboardButton(text=f"📚 {title}", callback_data=f"dict_view_{k}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Navigatsiya (Oldingi / Keyingi)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"dict_list_page_{page - 1}"))
    if end_idx < total:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"dict_list_page_{page + 1}"))

    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton(text="📚 Lug'at menyusi", callback_data="menu_dictionary"),
        InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "menu_dictionary")
async def cb_dictionary_menu(call: CallbackQuery, state: FSMContext):
    """Lug'at asosiy menyusi"""
    await state.clear()
    total_count = len(DICTIONARY_DATA)
    intro_text = (
        "📚 <b>Informatika lug‘ati bo'limi</b>\n\n"
        f"Bazamizda <b>{total_count} ta</b> eng zarur informatika terminlari, ularning batafsil ta'riflari "
        "va hayotiy misollari jamlangan.\n\n"
        "Quyidagi tugmalardan foydalaning yoki to'g'ridan-to'g'ri qidirayotgan terminingizni "
        "(masalan: <code>algoritm</code>, <code>kiberxavfsizlik</code>) yozib yuboring:"
    )
    await call.message.edit_text(
        text=intro_text,
        reply_markup=get_dictionary_menu_keyboard()
    )
    await call.answer()


@router.callback_query(F.data.startswith("dict_list_page_"))
async def cb_terms_page(call: CallbackQuery):
    """Terminlar ro'yxati sahifasi"""
    page = int(call.data.replace("dict_list_page_", ""))
    total_count = len(DICTIONARY_DATA)
    await call.message.edit_text(
        text=f"📋 <b>Barcha terminlar ro'yxati ({total_count} ta):</b>\nBatafsil ko'rish uchun ustiga bosing:",
        reply_markup=get_terms_list_keyboard(page)
    )
    await call.answer()


@router.callback_query(F.data == "dict_random")
async def cb_random_term(call: CallbackQuery):
    """Tasodifiy termin ko'rsatish"""
    all_keys = list(DICTIONARY_DATA.keys())
    if not all_keys:
        await call.answer("Lug'at bo'sh!", show_alert=True)
        return

    rand_key = random.choice(all_keys)
    card_text = format_term_card(rand_key)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎲 Boshqa termin", callback_data="dict_random"),
            InlineKeyboardButton(text="📚 Lug'at menyusi", callback_data="menu_dictionary"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ])
    await call.message.edit_text(text=card_text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "dict_search_prompt")
async def cb_search_prompt(call: CallbackQuery, state: FSMContext):
    """Termin qidirish uchun so'rov kiritishni so'rash"""
    await state.set_state(DictionaryStates.waiting_for_term)
    await call.message.edit_text(
        text=(
            "🔍 <b>Termin qidirish</b>\n\n"
            "Qidirayotgan tushunchangiz yoki so'zingizni yozib yuboring:\n"
            "<i>(Misol: algoritm, hardware, operatsion tizim, python, kiberxavfsizlik)</i>"
        ),
        reply_markup=get_cancel_keyboard("menu_dictionary")
    )
    await call.answer()


@router.callback_query(F.data.startswith("dict_view_"))
async def cb_view_single_term(call: CallbackQuery):
    """Alohida termin kartochkasini ochish"""
    term_key = call.data.replace("dict_view_", "")
    card_text = format_term_card(term_key)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Barcha terminlar", callback_data="dict_list_page_0"),
            InlineKeyboardButton(text="📚 Lug'at menyusi", callback_data="menu_dictionary"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ])
    await call.message.edit_text(text=card_text, reply_markup=kb)
    await call.answer()


@router.message(DictionaryStates.waiting_for_term)
async def process_term_search(message: Message, state: FSMContext):
    """Kiritilgan so'z bo'yicha lug'atdan qidirish"""
    await state.clear()
    query = message.text.strip()
    matches = find_terms_by_query(query)

    if not matches:
        await message.answer(
            text=(
                f"❓ <b>'{query}'</b> bo'yicha hech qanday termin topilmadi.\n\n"
                f"Iltimos, so'zning to'g'ri yozilganini tekshiring yoki ro'yxatdan qidiring."
            ),
            reply_markup=get_terms_list_keyboard(0)
        )
        return

    if len(matches) == 1:
        # Bitta aniq natija
        card_text = format_term_card(matches[0])
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Boshqa qidirish", callback_data="dict_search_prompt"),
                InlineKeyboardButton(text="📚 Lug'at menyusi", callback_data="menu_dictionary"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
            ]
        ])
        await message.answer(text=card_text, reply_markup=kb)
    else:
        # Bir nechta natija topilsa
        kb_rows = []
        for k in matches[:10]:
            title = DICTIONARY_DATA[k]["termin"]
            kb_rows.append([InlineKeyboardButton(text=f"📚 {title}", callback_data=f"dict_view_{k}")])
        kb_rows.append([InlineKeyboardButton(text="📚 Lug'at menyusi", callback_data="menu_dictionary")])

        await message.answer(
            text=f"🔍 <b>'{query}'</b> bo'yicha {len(matches)} ta termin topildi:\nTanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows)
        )
