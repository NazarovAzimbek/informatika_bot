import re

# Superscript raqamlar daraja ko'rsatkichlari uchun
SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '-': '⁻'
}

SUBSCRIPTS = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    '10': '₁₀', '16': '₁₆'
}


def to_sup(num: int) -> str:
    """Raqamni daraja belgisiga aylantirish (masalan: 5 -> ⁵)"""
    return "".join(SUPERSCRIPTS.get(c, c) for c in str(num))


def to_sub(base: int) -> str:
    """Asosni pastki indeksga aylantirish (masalan: 2 -> ₂)"""
    return SUBSCRIPTS.get(str(base), f"_{base}")


def validate_number(value_str: str, base: int) -> tuple[bool, str]:
    """
    Kiritilgan sonning berilgan sanoq sistemasiga mosligini tekshirish.
    Noto'g'ri bo'lsa, qaysi belgi xato ekanligini tushuntiradi.
    """
    clean_val = value_str.strip().upper()
    if not clean_val:
        return False, "❌ Son kiritilmadi! Iltimos, son kiriting."

    valid_chars = {
        2: set("01"),
        8: set("01234567"),
        10: set("0123456789"),
        16: set("0123456789ABCDEF")
    }

    if base not in valid_chars:
        return False, "❌ Noma'lum sanoq sistemasi!"

    allowed = valid_chars[base]
    invalid_chars = [ch for ch in clean_val if ch not in allowed]

    if invalid_chars:
        unique_invalid = list(dict.fromkeys(invalid_chars))
        bad_sample = ", ".join(f"'{c}'" for c in unique_invalid)
        
        base_desc = {
            2: "2-lik sanoq sistemasida faqat <b>0 va 1</b> raqamlaridan foydalaniladi.",
            8: "8-lik sanoq sistemasida faqat <b>0 dan 7 gacha</b> bo'lgan raqamlar ishlatiladi.",
            10: "10-lik sanoq sistemasida faqat <b>0 dan 9 gacha</b> bo'lgan raqamlar ishlatiladi.",
            16: "16-lik sanoq sistemasida <b>0–9 raqamlari va A, B, C, D, E, F</b> harflaridan foydalaniladi."
        }
        
        msg = (
            f"❌ <b>Xatolik!</b>\n\n"
            f"{base_desc[base]}\n\n"
            f"Siz kiritgan sonda ruxsat etilmagan belgi(lar): <b>{bad_sample}</b> mavjud.\n\n"
            f"Iltimos, qayta to'g'ri kiriting."
        )
        return False, msg

    return True, clean_val


def convert_any_to_dec_explanation(value_str: str, from_base: int) -> tuple[int, str]:
    """
    2, 8 yoki 16 likdan 10 likka o'tkazish va formula bilan tushuntirish
    """
    val = value_str.upper()
    n = len(val)
    parts = []
    calc_terms = []
    total = 0

    hex_map = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}

    for i, ch in enumerate(val):
        power = n - 1 - i
        digit_val = hex_map[ch] if ch in hex_map else int(ch)
        term_val = digit_val * (from_base ** power)
        total += term_val

        # Tushuntirish uchun ifoda
        if from_base == 16 and ch in hex_map:
            parts.append(f"{ch}(={digit_val})×{from_base}{to_sup(power)}")
        else:
            parts.append(f"{ch}×{from_base}{to_sup(power)}")
        
        calc_terms.append(str(term_val))

    formula_str = " + ".join(parts)
    terms_str = " + ".join(calc_terms)

    explanation = (
        f"<b>Hisoblash usuli (yoyilma shakli):</b>\n"
        f"<code>{val}{to_sub(from_base)} = {formula_str}</code>\n\n"
        f"= {terms_str}\n"
        f"= <b>{total}</b>"
    )
    return total, explanation


def convert_dec_to_any_explanation(dec_val: int, to_base: int) -> tuple[str, str]:
    """
    10 likdan 2, 8 yoki 16 likka ketma-ket bo'lish orqali o'tkazish
    """
    if dec_val == 0:
        return "0", f"0{to_sub(10)} = <b>0{to_sub(to_base)}</b>"

    hex_digits = "0123456789ABCDEF"
    rem_list = []
    steps = []
    temp = dec_val

    while temp > 0:
        qoldiq = temp % to_base
        butun = temp // to_base
        qoldiq_char = hex_digits[qoldiq]
        
        if to_base == 16 and qoldiq >= 10:
            steps.append(f"{temp} ÷ {to_base} = {butun} (qoldiq: {qoldiq} ➔ <b>{qoldiq_char}</b>)")
        else:
            steps.append(f"{temp} ÷ {to_base} = {butun} (qoldiq: <b>{qoldiq_char}</b>)")

        rem_list.append(qoldiq_char)
        temp = butun

    res_str = "".join(reversed(rem_list))
    steps_text = "\n".join(steps)

    explanation = (
        f"<b>Ketma-ket {to_base} ga bo'lish bosqichlari:</b>\n"
        f"<code>{steps_text}</code>\n\n"
        f"Qoldiqlarni <b>pastdan yuqoriga</b> qarab yozamiz:\n"
        f"✅ Natija: <b>{res_str}{to_sub(to_base)}</b>"
    )
    return res_str, explanation


def convert_number(value_str: str, from_base: int, to_base: int) -> tuple[bool, str]:
    """
    Sanoq sistemalari o'rtasida to'liq konvertatsiya va chiroyli tushuntirish beruvchi asosiy funksiya.
    """
    is_valid, validated_or_err = validate_number(value_str, from_base)
    if not is_valid:
        return False, validated_or_err

    val = validated_or_err

    # 1. Bir xil sistema tanlansa
    if from_base == to_base:
        return True, (
            f"🔢 <b>Sanoq sistemalari</b>\n\n"
            f"Siz bir xil sanoq sistemasini tanladingiz:\n"
            f"<b>{val}{to_sub(from_base)} = {val}{to_sub(to_base)}</b>"
        )

    # 2. X -> 10 ga o'tkazish
    if to_base == 10:
        total, exp = convert_any_to_dec_explanation(val, from_base)
        msg = (
            f"🔢 <b>Sanoq sistemalari</b>\n\n"
            f"<b>{val}{to_sub(from_base)}</b> ➔ <b>{total}{to_sub(10)}</b>\n\n"
            f"{exp}\n\n"
            f"✅ <b>Javob: {total}{to_sub(10)}</b>"
        )
        return True, msg

    # 3. 10 -> X ga o'tkazish
    if from_base == 10:
        dec_num = int(val)
        res_str, exp = convert_dec_to_any_explanation(dec_num, to_base)
        msg = (
            f"🔢 <b>Sanoq sistemalari</b>\n\n"
            f"<b>{val}{to_sub(10)}</b> ➔ <b>{res_str}{to_sub(to_base)}</b>\n\n"
            f"{exp}\n\n"
            f"✅ <b>Javob: {res_str}{to_sub(to_base)}</b>"
        )
        return True, msg

    # 4. X -> Y (masalan 2 -> 8, 2 -> 16, 8 -> 2, 8 -> 16, 16 -> 2, 16 -> 8)
    # Boshlang'ich 10 lik orqali bog'laymiz
    dec_val, exp1 = convert_any_to_dec_explanation(val, from_base)
    res_str, exp2 = convert_dec_to_any_explanation(dec_val, to_base)

    msg = (
        f"🔢 <b>Sanoq sistemalari</b>\n\n"
        f"<b>{val}{to_sub(from_base)}</b> ➔ <b>{res_str}{to_sub(to_base)}</b>\n\n"
        f"<b>1-bosqich: {from_base}-likdan 10-likka o'tkazamiz:</b>\n"
        f"{exp1}\n\n"
        f"<b>2-bosqich: 10-likdan {to_base}-likka o'tkazamiz:</b>\n"
        f"{exp2}\n\n"
        f"✅ <b>Yakuniy javob: {res_str}{to_sub(to_base)}</b>"
    )
    return True, msg


def detect_number_type(text: str) -> dict:
    """
    Foydalanuvchi yuborgan ixtiyoriy matn/raqamni qaysi sanoq sistemasiga mansub bo'lishi mumkinligini aniqlash.
    """
    clean = text.strip().upper()
    if not clean or len(clean) > 30:
        return {"detected": False}

    # Faqat 0 va 1 bo'lsa -> 2-lik (ikkilik)
    if re.fullmatch(r"[01]+", clean):
        return {
            "detected": True,
            "type": "binary",
            "base": 2,
            "value": clean,
            "prompt": (
                f"🔢 Siz <b>{clean}</b> sonini yubordingiz.\n\n"
                f"Bu son <b>2-lik (ikkilik)</b> sanoq sistemasida bo‘lishi mumkin.\n"
                f"Qaysi sistemaga o'tkazamiz?"
            ),
            "options": [
                ("2 ➔ 10", f"conv_2_10_{clean}"),
                ("2 ➔ 8", f"conv_2_8_{clean}"),
                ("2 ➔ 16", f"conv_2_16_{clean}")
            ]
        }

    # Faqat 0-9 raqamlari bo'lsa -> 10-lik (o'nlik)
    if re.fullmatch(r"[0-9]+", clean):
        return {
            "detected": True,
            "type": "decimal",
            "base": 10,
            "value": clean,
            "prompt": (
                f"🔢 Siz <b>{clean}</b> sonini yubordingiz.\n\n"
                f"<b>{clean}₁₀</b> ni qaysi sanoq sistemasiga o'tkazamiz?"
            ),
            "options": [
                ("10 ➔ 2", f"conv_10_2_{clean}"),
                ("10 ➔ 8", f"conv_10_8_{clean}"),
                ("10 ➔ 16", f"conv_10_16_{clean}")
            ]
        }

    # 16-lik (Hex) harflari (A-F) va raqamlar bo'lsa
    if re.fullmatch(r"[0-9A-F]+", clean):
        return {
            "detected": True,
            "type": "hex",
            "base": 16,
            "value": clean,
            "prompt": (
                f"🔢 Siz <b>{clean}</b> sonini yubordingiz.\n\n"
                f"Bu son <b>16-lik (Hex)</b> sanoq sistemasida bo'lishi mumkin.\n"
                f"Qaysi sistemaga o'tkazamiz?"
            ),
            "options": [
                ("16 ➔ 2", f"conv_16_2_{clean}"),
                ("16 ➔ 10", f"conv_16_10_{clean}"),
                ("16 ➔ 8", f"conv_16_8_{clean}")
            ]
        }

    return {"detected": False}


# ============================================================
# AXBOROT O'LCHOV BIRLIKLARI KONVERTORI
# ============================================================

INFO_UNITS = ["bit", "Byte", "KB", "MB", "GB", "TB", "PB"]

UNIT_POWERS = {
    "bit": -1,       # 1 bit = 1/8 Byte
    "Byte": 0,       # 1024^0 = 1 Byte
    "KB": 1,         # 1024^1 Byte
    "MB": 2,         # 1024^2 Byte
    "GB": 3,         # 1024^3 Byte
    "TB": 4,         # 1024^4 Byte
    "PB": 5          # 1024^5 Byte
}

UNIT_NAMES_UZ = {
    "bit": "bit",
    "Byte": "Bayt (Byte)",
    "KB": "Kilobayt (KB)",
    "MB": "Megabayt (MB)",
    "GB": "Gigabayt (GB)",
    "TB": "Terabayt (TB)",
    "PB": "Petabayt (PB)"
}


def to_bytes(value: float, unit: str) -> float:
    """Ixtiyoriy birlikdan Baytga o'tkazish"""
    if unit == "bit":
        return value / 8.0
    power = UNIT_POWERS[unit]
    return value * (1024 ** power)


def from_bytes(bytes_val: float, target_unit: str) -> float:
    """Baytdan maqsadli birlikka o'tkazish"""
    if target_unit == "bit":
        return bytes_val * 8.0
    power = UNIT_POWERS[target_unit]
    return bytes_val / (1024 ** power)


def format_unit_value(val: float) -> str:
    """Raqamlarni chiroyli formatda chiqarish"""
    if val == int(val):
        return f"{int(val):,}".replace(",", " ")
    elif val >= 0.0001:
        # 4-6 xonagacha yaxlitlash
        formatted = f"{val:.6f}".rstrip("0").rstrip(".")
        return formatted
    else:
        return f"{val:.8f}".rstrip("0").rstrip(".")


def convert_specific_unit(val: float, from_u: str, to_u: str) -> str:
    """
    Ikkita aniq birlik o'rtasida formula va qoida bilan o'tkazish
    """
    bytes_val = to_bytes(val, from_u)
    res = from_bytes(bytes_val, to_u)

    val_fmt = format_unit_value(val)
    res_fmt = format_unit_value(res)

    # Qoida va formula
    if from_u == to_u:
        formula_text = f"Bir xil birlik: {val_fmt} {from_u} = {res_fmt} {to_u}"
    elif from_u == "bit" and to_u == "Byte":
        formula_text = f"{val_fmt} ÷ 8 = <b>{res_fmt} Byte</b>\n<i>Qoida: Bitdan Baytga o'tishda 8 ga bo'linadi (1 Bayt = 8 bit).</i>"
    elif from_u == "Byte" and to_u == "bit":
        formula_text = f"{val_fmt} × 8 = <b>{res_fmt} bit</b>\n<i>Qoida: Baytdan bitga o'tishda 8 ga ko'paytiriladi.</i>"
    else:
        from_p = UNIT_POWERS[from_u]
        to_p = UNIT_POWERS[to_u]
        
        if from_p < to_p:
            diff = to_p - from_p
            formula_text = (
                f"{val_fmt} ÷ 1024{to_sup(diff)} = <b>{res_fmt} {to_u}</b>\n"
                f"<i>Qoida: Kichik birlikdan katta birlikka o'tishda 1024 ga bo'linadi.</i>"
            )
        else:
            diff = from_p - to_p
            formula_text = (
                f"{val_fmt} × 1024{to_sup(diff)} = <b>{res_fmt} {to_u}</b>\n"
                f"<i>Qoida: Katta birlikdan kichik birlikka o'tishda 1024 ga ko'paytiriladi.</i>"
            )

    return (
        f"💾 <b>Axborot birliklari konvertori</b>\n\n"
        f"<b>{val_fmt} {from_u}</b> ➔ <b>{res_fmt} {to_u}</b>\n\n"
        f"<b>Formula va hisoblash:</b>\n{formula_text}\n\n"
        f"✅ <b>Javob: {res_fmt} {to_u}</b>"
    )


def convert_all_units_summary(val: float, unit: str) -> str:
    """
    Berilgan qiymatni barcha asosiy birliklarda ko'rsatish
    """
    bytes_val = to_bytes(val, unit)
    val_fmt = format_unit_value(val)

    lines = []
    for u in INFO_UNITS:
        u_val = from_bytes(bytes_val, u)
        u_fmt = format_unit_value(u_val)
        if u == unit:
            lines.append(f"👉 <b>{u_fmt} {u}</b> <i>(kiritilgan qiymat)</i>")
        else:
            lines.append(f"• <b>{u}:</b> {u_fmt}")

    lines_text = "\n".join(lines)

    return (
        f"💾 <b>Axborot o‘lchov birliklari</b>\n\n"
        f"Kiritilgan qiymat: <b>{val_fmt} {unit}</b>\n\n"
        f"📊 <b>Barcha birliklardagi ifodasi:</b>\n"
        f"{lines_text}\n\n"
        f"📌 <i>Asosiy qoidalar:\n• 1 Byte = 8 bit\n• 1 KB = 1024 Byte\n• 1 MB = 1024 KB\n• 1 GB = 1024 MB\n• 1 TB = 1024 GB\n• 1 PB = 1024 TB</i>"
    )


def detect_info_unit_text(text: str) -> dict:
    """
    Matndan '100 MB', '5 GB', '1024 kb' kabi birlik yozuvlarini aniqlash
    """
    pattern = r"^\s*([0-9]+(?:[\.,][0-9]+)?)\s*(bit|byte|bayt|kb|mb|gb|tb|pb)\s*$"
    match = re.match(pattern, text.strip(), re.IGNORECASE)
    if not match:
        return {"detected": False}

    num_str = match.group(1).replace(",", ".")
    u_raw = match.group(2).lower()

    try:
        val = float(num_str)
    except ValueError:
        return {"detected": False}

    unit_map = {
        "bit": "bit",
        "byte": "Byte",
        "bayt": "Byte",
        "kb": "KB",
        "mb": "MB",
        "gb": "GB",
        "tb": "TB",
        "pb": "PB"
    }
    unit = unit_map.get(u_raw)
    if not unit:
        return {"detected": False}

    return {
        "detected": True,
        "value": val,
        "unit": unit
    }
