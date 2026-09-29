import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from keyboards import get_back_keyboard, get_cancel_keyboard

router = Router(name="computer_devices_router")


def load_devices() -> dict:
    """devices.json faylidan ma'lumotlarni o'qish"""
    try:
        with open(config.DEVICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


DEVICES_DATA = load_devices()

DEVICE_ICONS = {
    "cpu": "🧠",
    "ram": "⚡",
    "hdd": "💽",
    "ssd": "💾",
    "gpu": "🎮",
    "motherboard": "🖲",
    "monitor": "🖥",
    "keyboard": "⌨️",
    "mouse": "🖱",
    "printer": "🖨",
    "scanner": "📠",
    "webcam": "📷",
    "microphone": "🎙",
    "speaker": "🔊",
    "usb_flash": "🔌",
    "router": "🌐"
}


def format_device_card(dev_key: str) -> str:
    """Qurilma haqida chiroyli kartochka matni"""
    if dev_key not in DEVICES_DATA:
        return "❓ Qurilma topilmadi."

    info = DEVICES_DATA[dev_key]
    icon = DEVICE_ICONS.get(dev_key, "💻")

    return (
        f"{icon} <b>{info['nomi']}</b>\n\n"
        f"🎯 <b>Vazifasi:</b>\n{info['vazifasi']}\n\n"
        f"📌 <b>Turi:</b>\n{info['turi']}\n\n"
        f"💡 <b>Xususiyati / Afzalligi:</b>\n{info['afzalligi']}"
    )


def get_devices_categories_keyboard() -> InlineKeyboardMarkup:
    """Qurilmalar toifalari menyusi"""
    keyboard = [
        [
            InlineKeyboardButton(text="🧠 Ichki va hisoblash (CPU, GPU...)", callback_data="dev_cat_internal"),
        ],
        [
            InlineKeyboardButton(text="💾 Xotira (RAM, SSD, HDD, Flash)", callback_data="dev_cat_storage"),
        ],
        [
            InlineKeyboardButton(text="📥 Kiritish qurilmalari (Klaviatura, Skaner...)", callback_data="dev_cat_input"),
        ],
        [
            InlineKeyboardButton(text="📤 Chiqarish va aloqa (Monitor, Printer, Router...)", callback_data="dev_cat_output"),
        ],
        [
            InlineKeyboardButton(text="📋 Barcha 16 ta qurilma ro'yxati", callback_data="dev_list_all"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_devices_list_keyboard(devices_keys: list, back_callback: str = "menu_devices") -> InlineKeyboardMarkup:
    """Berilgan qurilmalar ro'yxati uchun tugmalar (2 tadan qator)"""
    keyboard = []
    row = []
    for k in devices_keys:
        if k in DEVICES_DATA:
            nomi = DEVICES_DATA[k]["nomi"].split(" (")[0]
            icon = DEVICE_ICONS.get(k, "💻")
            row.append(InlineKeyboardButton(text=f"{icon} {nomi}", callback_data=f"dev_view_{k}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "menu_devices")
async def cb_devices_menu(call: CallbackQuery, state: FSMContext):
    """Kompyuter qurilmalari asosiy menyusi"""
    await state.clear()
    intro_text = (
        "💻 <b>Kompyuter qurilmalari bo'limi</b>\n\n"
        "Kompyuter turli vazifalarni bajaruvchi apparat vositalari majmuasidan iborat.\n\n"
        "Quyidagi toifalardan birini tanlab, qurilmalarning vazifasi, turi va afzalliklari bilan tanishing:"
    )
    await call.message.edit_text(
        text=intro_text,
        reply_markup=get_devices_categories_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "dev_list_all")
async def cb_all_devices_list(call: CallbackQuery):
    """Barcha 16 ta qurilma ro'yxati"""
    all_keys = list(DEVICES_DATA.keys())
    await call.message.edit_text(
        text="📋 <b>Barcha 16 ta kompyuter qurilmalari:</b>\nBatafsil ma'lumot olish uchun tanlang:",
        reply_markup=get_devices_list_keyboard(all_keys, "menu_devices")
    )
    await call.answer()


@router.callback_query(F.data.startswith("dev_cat_"))
async def cb_device_category(call: CallbackQuery):
    """Kategoriya bo'yicha qurilmalar ro'yxati"""
    cat = call.data.replace("dev_cat_", "")

    cat_map = {
        "internal": (["cpu", "gpu", "motherboard"], "🧠 <b>Ichki va hisoblash qurilmalari:</b>"),
        "storage": (["ram", "ssd", "hdd", "usb_flash"], "💾 <b>Xotira qurilmalari:</b>"),
        "input": (["keyboard", "mouse", "scanner", "webcam", "microphone"], "📥 <b>Axborotni kiritish qurilmalari:</b>"),
        "output": (["monitor", "printer", "speaker", "router"], "📤 <b>Axborotni chiqarish va aloqa qurilmalari:</b>")
    }

    if cat not in cat_map:
        await call.answer()
        return

    keys, title = cat_map[cat]
    await call.message.edit_text(
        text=title,
        reply_markup=get_devices_list_keyboard(keys, "menu_devices")
    )
    await call.answer()


@router.callback_query(F.data.startswith("dev_view_"))
async def cb_view_single_device(call: CallbackQuery):
    """Alohida qurilma kartochkasini ochish"""
    dev_key = call.data.replace("dev_view_", "")
    card_text = format_device_card(dev_key)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Barcha qurilmalar", callback_data="dev_list_all"),
            InlineKeyboardButton(text="💻 Bo'lim menyusi", callback_data="menu_devices"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="menu_main")
        ]
    ])

    await call.message.edit_text(
        text=card_text,
        reply_markup=kb
    )
    await call.answer()


def find_device_by_text(query: str) -> tuple[bool, str]:
    """Matn orqali qurilmani qidirish"""
    clean = query.strip().lower()
    
    synonyms = {
        "protsessor": "cpu",
        "processor": "cpu",
        "markaziy protsessor": "cpu",
        "videokarta": "gpu",
        "ona plata": "motherboard",
        "ona_plata": "motherboard",
        "ekran": "monitor",
        "displey": "monitor",
        "klaviatura": "keyboard",
        "sichqoncha": "mouse",
        "skaner": "scanner",
        "veb kamera": "webcam",
        "veb-kamera": "webcam",
        "kolonka": "speaker",
        "karnay": "speaker",
        "fleshka": "usb_flash",
        "usb": "usb_flash",
        "marshrutizator": "router"
    }

    dev_key = None
    if clean in DEVICES_DATA:
        dev_key = clean
    elif clean in synonyms:
        dev_key = synonyms[clean]
    else:
        # substring qidiruv
        for k, info in DEVICES_DATA.items():
            if clean in k or clean in info["nomi"].lower():
                dev_key = k
                break

    if dev_key:
        return True, format_device_card(dev_key)
    return False, ""
