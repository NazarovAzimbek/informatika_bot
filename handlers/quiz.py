from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.quiz_service import get_random_quiz, get_question_by_id, load_all_questions
from keyboards import get_back_keyboard

router = Router(name="quiz_router")


class QuizStates(StatesGroup):
    in_quiz = State()


def get_quiz_intro_keyboard() -> InlineKeyboardMarkup:
    """Mini test asosiy menyusi tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="⚡ 5 talik tezkor test", callback_data="quiz_start_5"),
            InlineKeyboardButton(text="🎯 10 talik standart test", callback_data="quiz_start_10"),
        ],
        [
            InlineKeyboardButton(text="📚 20 talik chuqur test", callback_data="quiz_start_20"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def render_question_view(q_data: dict, current_num: int, total_num: int) -> tuple[str, InlineKeyboardMarkup]:
    """Savol matni va variantlar klaviaturasini tayyorlash"""
    letters = ["A", "B", "C", "D"]
    q_text = (
        f"🧠 <b>Mini test ({current_num}/{total_num})</b>\n\n"
        f"💡 <b>{q_data['question']}</b>"
    )

    keyboard = []
    for idx, opt in enumerate(q_data["options"]):
        lbl = f"{letters[idx]}) {opt}"
        keyboard.append([InlineKeyboardButton(text=lbl, callback_data=f"q_ans_{idx}")])

    keyboard.append([InlineKeyboardButton(text="❌ Testni to'xtatish", callback_data="quiz_stop")])
    return q_text, InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "menu_quiz")
async def cb_quiz_menu(call: CallbackQuery, state: FSMContext):
    """Mini test bo'limini ochish"""
    await state.clear()
    total_in_db = len(load_all_questions())
    intro_text = (
        "🧠 <b>Informatika mini test bo'limi</b>\n\n"
        f"Bazamizda jami <b>{total_in_db} ta</b> sifatli va maktab darsligiga mos savollar mavjud.\n\n"
        "Savollar tasodifiy tartibda beriladi va har bir javobdan so'ng to'g'ri/noto'g'ri "
        "ekanligi tushuntirib boriladi.\n\n"
        "Nechta savolli test topshirmoqchisiz?"
    )
    await call.message.edit_text(
        text=intro_text,
        reply_markup=get_quiz_intro_keyboard()
    )
    await call.answer()


@router.callback_query(F.data.startswith("quiz_start_"))
async def cb_start_quiz(call: CallbackQuery, state: FSMContext):
    """Testni boshlash"""
    count = int(call.data.split("_")[-1])
    questions = get_random_quiz(count)

    if not questions:
        await call.answer("Savollar topilmadi!", show_alert=True)
        return

    q_ids = [q["id"] for q in questions]

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        q_ids=q_ids,
        curr_idx=0,
        correct_count=0,
        total=len(q_ids)
    )

    first_q = questions[0]
    text, kb = render_question_view(first_q, 1, len(q_ids))
    await call.message.edit_text(text=text, reply_markup=kb)
    await call.answer()


@router.callback_query(QuizStates.in_quiz, F.data.startswith("q_ans_"))
async def cb_answer_question(call: CallbackQuery, state: FSMContext):
    """Foydalanuvchi variant tanlaganda tekshirish"""
    chosen_idx = int(call.data.replace("q_ans_", ""))
    data = await state.get_data()

    q_ids = data.get("q_ids", [])
    curr_idx = data.get("curr_idx", 0)
    correct_count = data.get("correct_count", 0)
    total = data.get("total", len(q_ids))

    if curr_idx >= len(q_ids):
        await call.answer()
        return

    q_id = q_ids[curr_idx]
    q_data = get_question_by_id(q_id)
    if not q_data:
        await call.answer()
        return

    is_correct = (chosen_idx == q_data["correct_index"])
    correct_opt_text = q_data["options"][q_data["correct_index"]]

    if is_correct:
        correct_count += 1
        await state.update_data(correct_count=correct_count)
        res_msg = (
            f"✅ <b>To‘g‘ri!</b>\n\n"
            f"<b>{correct_opt_text}</b> — to'g'ri javob.\n\n"
            f"💡 <i>{q_data['explanation']}</i>"
        )
    else:
        res_msg = (
            f"❌ <b>Noto‘g‘ri.</b>\n\n"
            f"To‘g‘ri javob: <b>{correct_opt_text}</b>\n\n"
            f"💡 <i>{q_data['explanation']}</i>"
        )

    is_last = (curr_idx + 1 >= total)
    next_btn_text = "🏁 Natijani ko'rish" if is_last else "➡️ Keyingi savol"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=next_btn_text, callback_data="quiz_next")],
        [InlineKeyboardButton(text="❌ Testni to'xtatish", callback_data="quiz_stop")]
    ])

    await call.message.edit_text(text=res_msg, reply_markup=kb)
    await call.answer()


@router.callback_query(QuizStates.in_quiz, F.data == "quiz_next")
async def cb_next_question(call: CallbackQuery, state: FSMContext):
    """Keyingi savolga o'tish yoki yakunlash"""
    data = await state.get_data()
    q_ids = data.get("q_ids", [])
    curr_idx = data.get("curr_idx", 0) + 1
    total = data.get("total", len(q_ids))
    correct_count = data.get("correct_count", 0)

    if curr_idx >= total:
        # Test yakunlandi
        await state.clear()
        wrong_count = total - correct_count
        percent = int((correct_count / total) * 100) if total > 0 else 0

        # Natijani SQLite bazasiga saqlaymiz
        import database
        await database.save_quiz_result(
            user_id=call.from_user.id,
            total=total,
            correct=correct_count,
            percentage=percent
        )

        if percent >= 90:
            comment = "🌟 Ajoyib natija! Informatika bilimingiz a'lo darajada!"
        elif percent >= 70:
            comment = "👍 Yaxshi natija! Bilimlaringiz mustahkam."
        elif percent >= 50:
            comment = "📖 Yomon emas, ammo mavzularni yana bir bor takrorlash foydadan xoli bo'lmaydi."
        else:
            comment = "💪 Tushkunlikka tushmang! Botdagi bo'limlarni o'rganib chiqib, yana urinib ko'ring."

        final_text = (
            f"🏁 <b>Test tugadi!</b>\n\n"
            f"📊 <b>Savollar:</b> {total} ta\n"
            f"✅ <b>To‘g‘ri javoblar:</b> {correct_count} ta\n"
            f"❌ <b>Noto‘g‘ri javoblar:</b> {wrong_count} ta\n"
            f"📈 <b>Natija:</b> {percent}%\n\n"
            f"{comment}"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Qayta topshirish", callback_data=f"quiz_start_{total}"),
                InlineKeyboardButton(text="📊 Mening natijalarim", callback_data="menu_stats"),
            ],
            [
                InlineKeyboardButton(text="🧠 Mini test menyusi", callback_data="menu_quiz"),
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main"),
            ]
        ])

        await call.message.edit_text(text=final_text, reply_markup=kb)
        await call.answer()
        return

    # Yangi savolni ko'rsatish
    await state.update_data(curr_idx=curr_idx)
    next_q_id = q_ids[curr_idx]
    q_data = get_question_by_id(next_q_id)

    text, kb = render_question_view(q_data, curr_idx + 1, total)
    await call.message.edit_text(text=text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "quiz_stop")
async def cb_stop_quiz(call: CallbackQuery, state: FSMContext):
    """Testni bekor qilish"""
    await state.clear()
    await call.message.edit_text(
        text="🛑 Test to'xtatildi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Mini test menyusi", callback_data="menu_quiz")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")]
        ])
    )
    await call.answer()
