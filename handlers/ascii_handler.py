from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import (
    get_ascii_menu,
    get_cancel_keyboard,
    get_after_ascii_keyboard,
    get_back_keyboard
)
from services.ascii_service import (
    char_to_ascii,
    code_to_ascii,
    get_ascii_info_text
)

router = Router(name="ascii_router")


class AsciiStates(StatesGroup):
    waiting_for_char = State()
    waiting_for_code = State()


ASCII_INTRO_TEXT = (
    "🔤 <b>ASCII bo'limi</b>\n\n"
    "Bu bo'limda siz istalgan belgining <b>ASCII kodi, Hex (16-lik) va Binary (2-lik)</b> "
    "kodlarini bilib olishingiz yoki aksincha, kod orqali belgini aniqlashingiz mumkin.\n\n"
    "Kerakli amalni tanlang:"
)


@router.callback_query(F.data == "menu_ascii")
async def cb_ascii_menu(call: CallbackQuery, state: FSMContext):
    """ASCII asosiy menyusi"""
    await state.clear()
    await call.message.edit_text(
        text=ASCII_INTRO_TEXT,
        reply_markup=get_ascii_menu()
    )
    await call.answer()


@router.callback_query(F.data == "ascii_info")
async def cb_ascii_info(call: CallbackQuery):
    """ASCII va Unicode haqida nazariy ma'lumot"""
    await call.message.edit_text(
        text=get_ascii_info_text(),
        reply_markup=get_cancel_keyboard("menu_ascii")
    )
    await call.answer()


@router.callback_query(F.data == "ascii_char_to_code")
async def cb_char_to_code_prompt(call: CallbackQuery, state: FSMContext):
    """Belgidan kod olishni so'rash"""
    await state.set_state(AsciiStates.waiting_for_char)
    await call.message.edit_text(
        text=(
            "🔤 <b>Belgi ➔ Kod</b>\n\n"
            "Iltimos, klaviaturadan biror belgi yoki harf yuboring:\n"
            "<i>(Misol: A, b, 7, @, ?, #)</i>"
        ),
        reply_markup=get_cancel_keyboard("menu_ascii")
    )
    await call.answer()


@router.message(AsciiStates.waiting_for_char)
async def process_char_input(message: Message, state: FSMContext):
    """Kiritilgan belgini tahlil qilish"""
    user_text = message.text
    if not user_text:
        await message.answer("❌ Iltimos, belgi yuboring:")
        return

    await state.clear()
    result_text = char_to_ascii(user_text)
    await message.answer(
        text=result_text,
        reply_markup=get_after_ascii_keyboard("char")
    )


@router.callback_query(F.data == "ascii_code_to_char")
async def cb_code_to_char_prompt(call: CallbackQuery, state: FSMContext):
    """Kiritilgan koddan belgi olishni so'rash"""
    await state.set_state(AsciiStates.waiting_for_code)
    await call.message.edit_text(
        text=(
            "🔢 <b>Kod ➔ Belgi</b>\n\n"
            "Iltimos, son (kod) kiriting:\n"
            "<i>(Misol: 65 — 'A', 97 — 'a', 48 — '0')</i>"
        ),
        reply_markup=get_cancel_keyboard("menu_ascii")
    )
    await call.answer()


@router.message(AsciiStates.waiting_for_code)
async def process_code_input(message: Message, state: FSMContext):
    """Kiritilgan kodni belgi holiga keltirish"""
    is_valid, result_text = code_to_ascii(message.text)
    if not is_valid:
        await message.answer(
            text=f"{result_text}\n\nQayta kiriting yoki bekor qiling:",
            reply_markup=get_cancel_keyboard("menu_ascii")
        )
        return

    await state.clear()
    await message.answer(
        text=result_text,
        reply_markup=get_after_ascii_keyboard("code")
    )
