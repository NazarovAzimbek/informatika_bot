from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import (
    get_number_systems_menu,
    get_cancel_keyboard,
    get_after_calc_keyboard,
    get_main_menu_keyboard
)
from services.converter import convert_number

router = Router(name="number_systems_router")


class NumberSystemStates(StatesGroup):
    waiting_for_number = State()


NS_INTRO_TEXT = (
    "🔢 <b>Sanoq sistemalari kalkulyatori</b>\n\n"
    "Bu bo'lim orqali <b>2-lik, 8-lik, 10-lik va 16-lik</b> sanoq sistemalari o'rtasida "
    "har qanday sonni bosqichma-bosqich yechimi va formulasi bilan o'tkazishingiz mumkin.\n\n"
    "Quyidagi yo'nalishlardan birini tanlang:\n"
    "<i>(Yoki to'g'ridan-to'g'ri istalgan sonni yozib yuborsangiz ham bo'ladi)</i>"
)


@router.callback_query(F.data == "menu_number_systems")
async def cb_number_systems_menu(call: CallbackQuery, state: FSMContext):
    """Sanoq sistemalari asosiy menyusini ko'rsatish"""
    await state.clear()
    await call.message.edit_text(
        text=NS_INTRO_TEXT,
        reply_markup=get_number_systems_menu()
    )
    await call.answer()


@router.callback_query(F.data.startswith("ns_"))
async def cb_choose_conversion_direction(call: CallbackQuery, state: FSMContext):
    """Konvertatsiya yo'nalishi tanlanganda (masalan: ns_2_10)"""
    parts = call.data.split("_")
    if len(parts) != 3:
        await call.answer()
        return

    from_base = int(parts[1])
    to_base = int(parts[2])

    await state.set_state(NumberSystemStates.waiting_for_number)
    await state.update_data(from_base=from_base, to_base=to_base)

    base_names = {
        2: "2-lik (ikkilik: faqat 0 va 1)",
        8: "8-lik (sakkizlik: 0 dan 7 gacha)",
        10: "10-lik (o'nlik: 0 dan 9 gacha)",
        16: "16-lik (o'n oltilik: 0-9 va A-F)"
    }

    prompt_text = (
        f"🔢 <b>{from_base} ➔ {to_base} konvertori</b>\n\n"
        f"Iltimos, <b>{base_names.get(from_base)}</b> dagi sonni kiriting:\n\n"
        f"<i>Misol: {'101101' if from_base == 2 else '45' if from_base == 10 else '55' if from_base == 8 else '2D'}</i>"
    )

    await call.message.edit_text(
        text=prompt_text,
        reply_markup=get_cancel_keyboard("menu_number_systems")
    )
    await call.answer()


@router.message(NumberSystemStates.waiting_for_number)
async def process_number_input(message: Message, state: FSMContext):
    """Foydalanuvchi son kiritganda uni tekshirish va hisoblash"""
    data = await state.get_data()
    from_base = data.get("from_base", 10)
    to_base = data.get("to_base", 2)

    user_text = message.text.strip()
    is_valid, result_msg = convert_number(user_text, from_base, to_base)

    if not is_valid:
        # Noto'g'ri kiritilgan bo'lsa, xatolikni ko'rsatib yana so'raymiz
        await message.answer(
            text=f"{result_msg}\n\nIltimos, sonni qayta kiriting yoki bekor qiling:",
            reply_markup=get_cancel_keyboard("menu_number_systems")
        )
        return

    # To'g'ri bo'lsa, holatni tozalaymiz va natijani yuboramiz
    await state.clear()
    await message.answer(
        text=result_msg,
        reply_markup=get_after_calc_keyboard(from_base, to_base)
    )


@router.callback_query(F.data.startswith("conv_"))
async def cb_quick_conversion(call: CallbackQuery, state: FSMContext):
    """Avto-aniqlashdan kelgan tezkor konvertatsiya tugmasi (masalan conv_2_10_101101)"""
    await state.clear()
    parts = call.data.split("_")
    if len(parts) != 4:
        await call.answer()
        return

    from_base = int(parts[1])
    to_base = int(parts[2])
    val = parts[3]

    _, result_msg = convert_number(val, from_base, to_base)
    await call.message.edit_text(
        text=result_msg,
        reply_markup=get_after_calc_keyboard(from_base, to_base)
    )
    await call.answer()
