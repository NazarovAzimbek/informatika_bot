CONTROL_CHARS = {
    0: "NUL (Null belgi)",
    7: "BEL (Qo'ng'iroq / Ovozli signal)",
    8: "BS (Backspace / O'chirish)",
    9: "TAB (Gorizontal tabulyatsiya)",
    10: "LF (Yangi qator / Line Feed)",
    13: "CR (Qator boshiga qaytish / Carriage Return)",
    27: "ESC (Escape)",
    32: "SP (Bo'sh joy / Probel)",
    127: "DEL (Delete / O'chirish)"
}


def get_ascii_info_text() -> str:
    """ASCII standarti haqida qisqacha ma'lumot"""
    return (
        "🔤 <b>ASCII va Unicode haqida qisqacha:</b>\n\n"
        "• <b>ASCII (American Standard Code for Information Interchange)</b> — "
        "1963-yilda qabul qilingan bo'lib, 7 bitdan (0 dan 127 gacha, jami 128 ta belgi) iborat.\n"
        "  - 0–31 va 127: Boshqaruvchi belgilar (masalan: Enter, Tab, Probel);\n"
        "  - 48–57: '0'–'9' raqamlari;\n"
        "  - 65–90: 'A'–'Z' katta lotin harflari;\n"
        "  - 97–122: 'a'–'z' kichik lotin harflari;\n\n"
        "• <b>Unicode (UTF-8)</b> — Dunyodagi barcha tillar (jumladan o'zbekcha o‘, g‘ harflari, "
        "kirill, arab, xitoy iyerogliflari va emojilar)ni ifodalash uchun yaratilgan zamonaviy universal standart."
    )


def char_to_ascii(char: str) -> str:
    """Belgidan ASCII/Unicode ma'lumotlarini olish"""
    if not char:
        return "❌ Belgi kiritilmadi!"

    target_char = char[0]  # birinchi belgi
    code = ord(target_char)
    hex_code = f"{code:02X}"
    bin_code = f"{code:08b}" if code <= 255 else f"{code:b}"

    # Diapazon izohi
    if code <= 127:
        desc = "✅ Standart 7-bitli ASCII diapazoni (0–127)"
    elif code <= 255:
        desc = "ℹ️ Kengaytirilgan 8-bitli ASCII / ANSI diapazoni (128–255)"
    else:
        desc = "🌐 Unicode (Standart ASCII dan tashqarida, ko'p baytli belgi)"

    ctrl_desc = f" ({CONTROL_CHARS[code]})" if code in CONTROL_CHARS else ""

    return (
        f"🔤 <b>ASCII ma'lumoti</b>\n\n"
        f"<b>Belgi:</b> <code>{target_char}</code>{ctrl_desc}\n"
        f"<b>ASCII (Dec) kodi:</b> <code>{code}</code>\n"
        f"<b>Hex (16-lik):</b> <code>{hex_code}</code>\n"
        f"<b>Binary (2-lik):</b> <code>{bin_code}</code>\n\n"
        f"📌 <b>Holati:</b> {desc}"
    )


def code_to_ascii(code_str: str) -> tuple[bool, str]:
    """Kiritilgan sondan belgi hosil qilish"""
    clean = code_str.strip()
    try:
        code = int(clean)
    except ValueError:
        return False, "❌ Iltimos, faqat butun son kiriting (masalan: <code>65</code>)."

    if code < 0 or code > 1114111:
        return False, "❌ Son diapazondan tashqarida! 0 dan 127 gacha (yoki Unicode uchun 1114111 gacha) son kiriting."

    char = chr(code)
    hex_code = f"{code:02X}"
    bin_code = f"{code:08b}" if code <= 255 else f"{code:b}"

    ctrl_desc = f" <i>({CONTROL_CHARS[code]})</i>" if code in CONTROL_CHARS else ""

    if code <= 127:
        desc = "Standart ASCII (0–127)"
    else:
        desc = "Unicode standarti"

    return True, (
        f"🔤 <b>ASCII kodi: {code}</b>\n\n"
        f"<b>Belgi:</b> <code>{char}</code>{ctrl_desc}\n"
        f"<b>Hex:</b> <code>{hex_code}</code>\n"
        f"<b>Binary:</b> <code>{bin_code}</code>\n"
        f"<b>Turi:</b> {desc}\n\n"
        f"✅ <b>Natija: {code} ➔ {char}</b>"
    )
