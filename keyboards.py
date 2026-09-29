from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu uchun inline tugmalar klaviaturasi"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔢 Sanoq sistemalari", callback_data="menu_number_systems"),
            InlineKeyboardButton(text="💾 Axborot birliklari", callback_data="menu_info_units"),
        ],
        [
            InlineKeyboardButton(text="🔤 ASCII", callback_data="menu_ascii"),
            InlineKeyboardButton(text="📁 Fayl kengaytmalari", callback_data="menu_file_ext"),
        ],
        [
            InlineKeyboardButton(text="💻 Kompyuter qurilmalari", callback_data="menu_devices"),
            InlineKeyboardButton(text="🧠 Mini test", callback_data="menu_quiz"),
        ],
        [
            InlineKeyboardButton(text="📚 Informatika lug‘ati", callback_data="menu_dictionary"),
            InlineKeyboardButton(text="📊 Mening natijalarim", callback_data="menu_stats"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="menu_about"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Har bir bo'limdan asosiy menyuga qaytish tugmasi"""
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard(back_callback: str = "menu_number_systems") -> InlineKeyboardMarkup:
    """Jarayonni bekor qilish tugmasi"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=back_callback)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_number_systems_menu() -> InlineKeyboardMarkup:
    """Sanoq sistemalari yo'nalishlari inline menyusi"""
    keyboard = [
        [
            InlineKeyboardButton(text="2 ➔ 10", callback_data="ns_2_10"),
            InlineKeyboardButton(text="10 ➔ 2", callback_data="ns_10_2"),
        ],
        [
            InlineKeyboardButton(text="2 ➔ 8", callback_data="ns_2_8"),
            InlineKeyboardButton(text="8 ➔ 2", callback_data="ns_8_2"),
        ],
        [
            InlineKeyboardButton(text="2 ➔ 16", callback_data="ns_2_16"),
            InlineKeyboardButton(text="16 ➔ 2", callback_data="ns_16_2"),
        ],
        [
            InlineKeyboardButton(text="8 ➔ 10", callback_data="ns_8_10"),
            InlineKeyboardButton(text="10 ➔ 8", callback_data="ns_10_8"),
        ],
        [
            InlineKeyboardButton(text="16 ➔ 10", callback_data="ns_16_10"),
            InlineKeyboardButton(text="10 ➔ 16", callback_data="ns_10_16"),
        ],
        [
            InlineKeyboardButton(text="8 ➔ 16", callback_data="ns_8_16"),
            InlineKeyboardButton(text="16 ➔ 8", callback_data="ns_16_8"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_after_calc_keyboard(from_base: int, to_base: int) -> InlineKeyboardMarkup:
    """Sanoq sistemasi hisoblangandan keyingi tugmalar"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔁 Yana hisoblash", callback_data=f"ns_{from_base}_{to_base}"),
            InlineKeyboardButton(text="🔢 Bo'lim menyusi", callback_data="menu_number_systems"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_info_units_menu() -> InlineKeyboardMarkup:
    """Axborot birliklari inline menyusi"""
    keyboard = [
        [
            InlineKeyboardButton(text="💾 MB ➔ KB", callback_data="unit_MB_KB"),
            InlineKeyboardButton(text="💾 GB ➔ MB", callback_data="unit_GB_MB"),
        ],
        [
            InlineKeyboardButton(text="💾 TB ➔ GB", callback_data="unit_TB_GB"),
            InlineKeyboardButton(text="💾 KB ➔ Byte", callback_data="unit_KB_Byte"),
        ],
        [
            InlineKeyboardButton(text="💾 Byte ➔ bit", callback_data="unit_Byte_bit"),
            InlineKeyboardButton(text="💾 bit ➔ Byte", callback_data="unit_bit_Byte"),
        ],
        [
            InlineKeyboardButton(text="💾 GB ➔ KB", callback_data="unit_GB_KB"),
            InlineKeyboardButton(text="💾 MB ➔ Byte", callback_data="unit_MB_Byte"),
        ],
        [
            InlineKeyboardButton(text="📊 Har qanday birlikni to'liq ko'rish", callback_data="unit_custom_all")
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_unit_selection_keyboard() -> InlineKeyboardMarkup:
    """To'liq ko'rish uchun birlik tanlash tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="bit", callback_data="u_sel_bit"),
            InlineKeyboardButton(text="Byte", callback_data="u_sel_Byte"),
            InlineKeyboardButton(text="KB", callback_data="u_sel_KB"),
        ],
        [
            InlineKeyboardButton(text="MB", callback_data="u_sel_MB"),
            InlineKeyboardButton(text="GB", callback_data="u_sel_GB"),
            InlineKeyboardButton(text="TB", callback_data="u_sel_TB"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="menu_info_units")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_after_unit_calc_keyboard(from_u: str = None, to_u: str = None) -> InlineKeyboardMarkup:
    """Birlik hisoblangandan keyingi tugmalar"""
    keyboard = []
    if from_u and to_u:
        keyboard.append([
            InlineKeyboardButton(text="🔁 Yana hisoblash", callback_data=f"unit_{from_u}_{to_u}"),
            InlineKeyboardButton(text="💾 Bo'lim menyusi", callback_data="menu_info_units"),
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="💾 Bo'lim menyusi", callback_data="menu_info_units"),
        ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_ascii_menu() -> InlineKeyboardMarkup:
    """ASCII bo'limi menyusi"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔤 Belgi ➔ Kod (A ➔ 65)", callback_data="ascii_char_to_code"),
            InlineKeyboardButton(text="🔢 Kod ➔ Belgi (65 ➔ A)", callback_data="ascii_code_to_char"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ ASCII va Unicode haqida", callback_data="ascii_info"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_after_ascii_keyboard(mode: str = "char") -> InlineKeyboardMarkup:
    """ASCII hisoblangandan keyingi tugmalar"""
    cb = "ascii_char_to_code" if mode == "char" else "ascii_code_to_char"
    keyboard = [
        [
            InlineKeyboardButton(text="🔁 Yana tekshirish", callback_data=cb),
            InlineKeyboardButton(text="🔤 ASCII menyusi", callback_data="menu_ascii"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
