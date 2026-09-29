from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.converter import (
    detect_number_type,
    detect_info_unit_text,
    convert_all_units_summary
)
from handlers.file_extensions import find_extension_info, get_after_ext_keyboard
from handlers.computer_devices import find_device_by_text
from handlers.dictionary import find_terms_by_query, format_term_card, DICTIONARY_DATA
from keyboards import get_main_menu_keyboard, get_after_unit_calc_keyboard

router = Router(name="common_router")


@router.message(F.text)
async def process_any_text(message: Message):
    """
    Foydalanuvchi ixtiyoriy matn yoki son yuborganda avtomatik aniqlash
    """
    text = message.text.strip()

    # 1. Axborot birliklari (masalan: 100 MB, 5 GB) aniqlash
    info_detection = detect_info_unit_text(text)
    if info_detection["detected"]:
        val = info_detection["value"]
        u = info_detection["unit"]
        summary = convert_all_units_summary(val, u)
        await message.answer(
            text=summary,
            reply_markup=get_after_unit_calc_keyboard()
        )
        return

    # 2. Sanoq sistemasi bo'yicha son aniqlash (101101, 255, 1A3)
    ns_detection = detect_number_type(text)
    if ns_detection["detected"]:
        buttons = []
        row = []
        for label, cb in ns_detection["options"]:
            row.append(InlineKeyboardButton(text=label, callback_data=cb))
        buttons.append(row)
        buttons.append([InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")])

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(
            text=ns_detection["prompt"],
            reply_markup=kb
        )
        return

    # 3. Fayl kengaytmasi yoki fayl nomi (masalan: .docx yoki rasm.png)
    if text.startswith(".") or ("." in text and len(text.split(".")[-1]) <= 6 and " " not in text):
        found, ext_msg = find_extension_info(text)
        if found:
            await message.answer(
                text=ext_msg,
                reply_markup=get_after_ext_keyboard()
            )
            return

    # 4. Kompyuter qurilmasi qidiruvi (masalan: SSD, CPU, klaviatura)
    found_dev, dev_card = find_device_by_text(text)
    if found_dev:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Barcha qurilmalar", callback_data="dev_list_all"),
                InlineKeyboardButton(text="💻 Bo'lim menyusi", callback_data="menu_devices"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
            ]
        ])
        await message.answer(text=dev_card, reply_markup=kb)
        return

    # 5. Informatika lug'ati qidiruvi (masalan: algoritm, kiberxavfsizlik, python)
    term_matches = find_terms_by_query(text)
    if term_matches:
        if len(term_matches) == 1:
            card_text = format_term_card(term_matches[0])
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📚 Lug'at menyusi", callback_data="menu_dictionary"),
                    InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
                ]
            ])
            await message.answer(text=card_text, reply_markup=kb)
            return
        else:
            kb_rows = []
            for k in term_matches[:6]:
                title = DICTIONARY_DATA[k]["termin"]
                kb_rows.append([InlineKeyboardButton(text=f"📚 {title}", callback_data=f"dict_view_{k}")])
            kb_rows.append([InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")])
            await message.answer(
                text=f"🔍 <b>'{text}'</b> bo'yicha lug'atdan topilgan terminlar:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows)
            )
            return

    # 6. Tushunarsiz boshqa matnlar uchun muloyim tushuntirish
    await message.answer(
        text=(
            "⚠️ <b>Ma'lumotni tushunib bo‘lmadi.</b>\n\n"
            "Iltimos, menyudan kerakli bo‘limni tanlang yoki "
            "/menu buyrug‘idan foydalaning."
        ),
        reply_markup=get_main_menu_keyboard()
    )
