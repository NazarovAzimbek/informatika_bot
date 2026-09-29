from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import (
    get_info_units_menu,
    get_cancel_keyboard,
    get_unit_selection_keyboard,
    get_after_unit_calc_keyboard
)
from services.converter import (
    convert_specific_unit,
    convert_all_units_summary,
    UNIT_NAMES_UZ
)

router = Router(name="information_units_router")


class InfoUnitsStates(StatesGroup):
    waiting_for_value = State()
    waiting_for_custom_val = State()


INFO_INTRO_TEXT = (
    "💾 <b>Axborot o‘lchov birliklari konvertori</b>\n\n"
    "Bu bo'limda <b>bit, Byte, KB, MB, GB, TB, PB</b> birliklarini o'zaro "
    "aniq formula va qoidalar bilan o'tkazishingiz mumkin.\n\n"
    "Quyidagi standart yo'nalishlardan birini tanlang:\n"
    "<i>(Yoki shunchaki masalan <code>100 MB</code> yoki <code>5 GB</code> deb yozib yuboring)</i>"
)


@router.callback_query(F.data == "menu_info_units")
async def cb_info_units_menu(call: CallbackQuery, state: FSMContext):
    """Axborot birliklari asosiy menyusi"""
    await state.clear()
    await call.message.edit_text(
        text=INFO_INTRO_TEXT,
        reply_markup=get_info_units_menu()
    )
    await call.answer()


@router.callback_query(F.data.startswith("unit_custom_all"))
async def cb_unit_custom_all(call: CallbackQuery, state: FSMContext):
    """Foydalanuvchiga birlik tanlatish"""
    await state.clear()
    await call.message.edit_text(
        text="📊 <b>Barcha birliklarda ko'rish</b>\n\nQaysi birlikdagi qiymatni kiritmoqchisiz? Tanlang:",
        reply_markup=get_unit_selection_keyboard()
    )
    await call.answer()


@router.callback_query(F.data.startswith("u_sel_"))
async def cb_unit_selected(call: CallbackQuery, state: FSMContext):
    """Tanlangan birlik uchun qiymat so'rash"""
    selected_unit = call.data.replace("u_sel_", "")
    await state.set_state(InfoUnitsStates.waiting_for_custom_val)
    await state.update_data(unit=selected_unit)

    await call.message.edit_text(
        text=(
            f"💾 Siz <b>{UNIT_NAMES_UZ.get(selected_unit, selected_unit)}</b> birligini tanladingiz.\n\n"
            f"Iltimos, son qiymatini kiriting (masalan: <code>100</code> yoki <code>2.5</code>):"
        ),
        reply_markup=get_cancel_keyboard("menu_info_units")
    )
    await call.answer()


@router.message(InfoUnitsStates.waiting_for_custom_val)
async def process_custom_unit_input(message: Message, state: FSMContext):
    """Tanlangan birlik bo'yicha barcha jadvalni chiqarish"""
    data = await state.get_data()
    unit = data.get("unit", "MB")

    try:
        val = float(message.text.strip().replace(",", "."))
        if val < 0:
            raise ValueError()
    except ValueError:
        await message.answer(
            text="❌ Noto'g'ri son kiritildi! Iltimos, musbat son kiriting (masalan: <code>100</code> yoki <code>1.5</code>):",
            reply_markup=get_cancel_keyboard("menu_info_units")
        )
        return

    await state.clear()
    summary_text = convert_all_units_summary(val, unit)
    await message.answer(
        text=summary_text,
        reply_markup=get_after_unit_calc_keyboard()
    )


@router.callback_query(F.data.startswith("unit_"))
async def cb_specific_unit_pair(call: CallbackQuery, state: FSMContext):
    """Aniq juftlik tanlanganda (masalan: unit_MB_KB)"""
    parts = call.data.split("_")
    if len(parts) != 3:
        await call.answer()
        return

    from_u = parts[1]
    to_u = parts[2]

    await state.set_state(InfoUnitsStates.waiting_for_value)
    await state.update_data(from_u=from_u, to_u=to_u)

    await call.message.edit_text(
        text=(
            f"💾 <b>{from_u} ➔ {to_u} konvertori</b>\n\n"
            f"Iltimos, <b>{from_u}</b> miqdorini kiriting:\n\n"
            f"<i>Misol: 100 yoki 0.5</i>"
        ),
        reply_markup=get_cancel_keyboard("menu_info_units")
    )
    await call.answer()


@router.message(InfoUnitsStates.waiting_for_value)
async def process_pair_unit_input(message: Message, state: FSMContext):
    """Juftlik uchun kiritilgan sonni hisoblash"""
    data = await state.get_data()
    from_u = data.get("from_u", "MB")
    to_u = data.get("to_u", "KB")

    try:
        val = float(message.text.strip().replace(",", "."))
        if val < 0:
            raise ValueError()
    except ValueError:
        await message.answer(
            text="❌ Noto'g'ri son kiritildi! Iltimos, musbat son kiriting (masalan: <code>100</code>):",
            reply_markup=get_cancel_keyboard("menu_info_units")
        )
        return

    await state.clear()
    result_text = convert_specific_unit(val, from_u, to_u)
    await message.answer(
        text=result_text,
        reply_markup=get_after_unit_calc_keyboard(from_u, to_u)
    )
